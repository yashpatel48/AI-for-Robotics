import asyncio
import os
from nats.aio.client import Client as NATS

# Your host gateway IP (container → host)
HOST_NATS_IP = "172.22.48.1"   # keep the value you confirmed earlier


async def main():
    nc = NATS()

    # Connect to NATS running on the host
    await nc.connect("127.0.0.1:4222")
    print("[BRIDGE] Connected to NATS")

    async def handle_cmd(msg):
        cmd = msg.data.decode()
        print(f"[BRIDGE] Received cmd: {cmd}")

        # Source ROS2 Jazzy + workspace overlay before executing command
        ros_env_cmd = (
            "source /opt/ros/jazzy/setup.bash && "
            "source /overlay_ws/install/setup.bash 2>/dev/null || true && "
            f"{cmd}"
        )

        try:
            # Run inside bash so "source" works
            output = os.popen(f"bash -c \"{ros_env_cmd}\"").read()
        except Exception as e:
            output = f"[BRIDGE ERROR] {e}"

        print("[BRIDGE] Sending reply...")
        await nc.publish("ros.reply", output.encode())

    # Subscribe to LLM→ROS commands
    await nc.subscribe("ros.cmd", cb=handle_cmd)
    print("[BRIDGE] Listening on ros.cmd...")

    # Keep bridge alive
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
