import subprocess

def run_ros_command(cmd: str) -> str:
    """
    Execute ROS 2 CLI commands inside the local ROS 2 environment.
    Automatically maps ROS 1 commands to ROS 2 equivalents.
    """
    
    # Mapping table ROS1 → ROS2
    cmd_map = {
        "rostopic list": "ros2 topic list",
        "rostopic echo": "ros2 topic echo",
        "rostopic info": "ros2 topic info",
        "rosnode list": "ros2 node list",
        "rosservice list": "ros2 service list",
        "rosservice info": "ros2 service info"
    }

    # Auto-convert ROS1 commands to ROS2
    for old, new in cmd_map.items():
        if cmd.startswith(old):
            cmd = cmd.replace(old, new)

    try:
        result = subprocess.check_output(
            cmd.split(),
            stderr=subprocess.STDOUT
        )
        return result.decode()
    except Exception as e:
        return f"[Executor Error] {e}"
