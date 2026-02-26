## Code Folder Overview

This folder contains the complete implementation of the ROSA system. Each file has a clearly defined role and contributes to building a decoupled AI-agent architecture for safe interaction with a ROS2-based robotic environment.

---

### `client.py`
Acts as the user-facing entry point.

- Accepts natural language input from the terminal
- Sends input to the ROSA Agent for interpretation
- Displays responses or execution results returned by the system

This file does not interpret commands or interact with ROS directly.

---

### `rosa_agent.py`
Defines the core ROSA Agent.

- Uses **pydantic.ai** and an LLM to interpret user input
- Classifies input as normal conversation, ROS2 CLI command, or navigation command
- Converts valid requests into structured commands

The agent never executes ROS commands directly.

---

### `react_prompt.txt`
Defines behavioral constraints for the ROSA Agent.

- Enforces ReAct-style behavior
- Prevents explanations, follow-up questions, or chained actions
- Restricts the agent to producing a single, well-defined action per input

Keeping this separate allows behavior changes without modifying code.

---

### `nats_client.py`
Implements the messaging interface using NATS.

- Connects to the NATS server
- Publishes structured commands
- Waits for execution results using request–reply messaging

This file ensures the AI agent is fully decoupled from ROS execution.

---

### `ros_bridge.py`
Serves as the execution boundary between AI and ROS.

- Subscribes to commands received via NATS
- Executes ROS2 CLI or navigation actions
- Sends execution output back through NATS

This is the only file that interacts directly with ROS2.

---

### `test.py`
A lightweight sanity test.

- Verifies ROSA Agent startup
- Confirms connectivity with the NATS server
- Used before integrating ROS execution

---

### `test_ros_bridge.py`
An end-to-end integration test.

- Sends a command through NATS
- Confirms execution by the ROS Bridge
- Verifies that responses are correctly returned

This validates the complete execution pipeline.

---

### `requirements.txt`
Lists all Python dependencies required to run the project, ensuring reproducibility in a clean environment.

---

### Summary
Together, these files demonstrate a modular and safe architecture where natural language interpretation, communication, and ROS execution are clearly separated. This structure aligns with the goals of building decoupled AI agents for robotics.


