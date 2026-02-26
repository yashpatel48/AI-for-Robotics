# executor.py
import nats

async def run_ros_command(cmd):
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("ros.cmd", cmd.encode())
    await nc.close()
    return f"[sent to ros]: {cmd}"
