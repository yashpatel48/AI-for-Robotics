import asyncio
from nats.aio.client import Client as NATS

async def test():
    nc = NATS()
    await nc.connect("nats://127.0.0.1:4222")

    future = asyncio.Future()

    async def cb(msg):
        future.set_result(msg.data.decode())

    await nc.subscribe("ros.reply", cb=cb)

    print("SENDING TEST MESSAGE...")
    await nc.publish("ros.cmd", b"echo hello")

    print("WAITING FOR REPLY...")
    reply = await future
    print("GOT:", reply)

asyncio.run(test())
