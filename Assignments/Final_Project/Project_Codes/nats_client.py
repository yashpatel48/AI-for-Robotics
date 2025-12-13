import asyncio
from nats.aio.client import Client as NATS

async def send_cmd(cmd: str):
    nc = NATS()
    await nc.connect("127.0.0.1:4222")

    # --- Subscribe BEFORE publishing (fixes race condition) ---
    future = asyncio.Future()

    async def handler(msg):
        if not future.done():
            future.set_result(msg.data.decode())

    sid = await nc.subscribe("ros.reply", cb=handler)

    # --- Now publish the command ---
    await nc.publish("ros.cmd", cmd.encode())

    # Wait for reply
    result = await future

    # Cleanup
    await nc.unsubscribe(sid)
    await nc.close()

    return result
