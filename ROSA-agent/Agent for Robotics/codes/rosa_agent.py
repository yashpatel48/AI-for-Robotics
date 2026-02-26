import os
import re
import json
import asyncio
from math import radians
from pydantic_ai import Agent
from pydantic_ai.agent import RunContext
from nats.aio.client import Client as NATS

# Load the ReAct system prompt used by the agent
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "react_prompt.txt")

with open(PROMPT_PATH) as f:
    system_prompt = f.read()

# NATS connection settings for the ROS bridge
NATS_HOST = "127.0.0.1"
NATS_PORT = 4222

# Send regular ROS2 CLI commands over NATS
async def send_nats(cmd: str) -> str:
    nc = NATS()
    await nc.connect(f"nats://{NATS_HOST}:{NATS_PORT}")

    fut = asyncio.Future()

    async def handler(msg):
        if not fut.done():
            fut.set_result(msg.data.decode())

    # Subscribe first so we don't miss the reply
    await nc.subscribe("ros.reply", cb=handler)
    await nc.flush()

    await nc.publish("ros.cmd", cmd.encode())
    result = await fut
    await nc.close()
    return result

# Send navigation actions as structured JSON
async def send_nats_action(action_dict: dict) -> str:
    nc = NATS()
    await nc.connect(f"nats://{NATS_HOST}:{NATS_PORT}")

    fut = asyncio.Future()

    async def handler(msg):
        if not fut.done():
            fut.set_result(msg.data.decode())

    await nc.subscribe("ros.reply.action", cb=handler)
    await nc.flush()

    await nc.publish(
        "ros.cmd.action",
        json.dumps(action_dict).encode()
    )

    result = await fut
    await nc.close()
    return result

# Create the LLM agent
agent = Agent(
    system_prompt=system_prompt,
    model="groq:llama-3.1-8b-instant",
    model_settings={"tool_choice": "none"}
)

# Tool for executing ROS2 CLI commands
@agent.tool
async def ros(ctx: RunContext, cmd: str) -> str:
    # Guard against non-ROS commands
    if not cmd.startswith("ros2 "):
        return "[ERROR] ROS2 command must start with 'ros2 '"
    return await send_nats(cmd)

# Parse natural language navigation into ROS-compatible actions
def parse_instruction(text: str):
    t = text.lower()

    # Handle rotation commands
    if "turn" in t or "rotate" in t:
        right = "right" in t

        match = re.search(r'(\d+)', t)
        angle_deg = float(match.group(1)) if match else 90.0
        angle_rad = radians(angle_deg) * (-1 if right else 1)

        return {
            "action_type": "spin",
            "goal": {
                "angle": angle_rad
            }
        }

    # Handle movement commands
    if "move" in t or "go" in t or "drive" in t:

        # Absolute position navigation
        if "x" in t and "y" in t:
            nums = re.findall(r'[-+]?\d*\.\d+|\d+', t)
            if len(nums) >= 2:
                return {
                    "action_type": "navigate_to_pose",
                    "goal": {
                        "x": float(nums[0]),
                        "y": float(nums[1]),
                        "yaw": 0.0
                    }
                }

        # Relative forward / backward motion
        backward = "back" in t or "backward" in t

        match = re.search(r'(\d+(\.\d+)?)', t)
        dist = float(match.group(1)) if match else 0.5
        dist = -abs(dist) if backward else abs(dist)

        return {
            "action_type": "backup",
            "goal": {
                "distance": dist
            }
        }

    # Fallback to a small relative move
    return {
        "action_type": "relative_move",
        "goal": {
            "x": 0.1,
            "y": 0.0
        }
    }

# Tool for navigation commands
@agent.tool
async def nav(ctx: RunContext, instruction: str) -> str:
    action_json = parse_instruction(instruction)
    return await send_nats_action(action_json)
