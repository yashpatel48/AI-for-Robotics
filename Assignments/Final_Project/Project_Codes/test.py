import asyncio
from nats.aio.client import Client as NATS

async def test():
    nc = NATS()
    print("▶ Trying to connect to NATS at 127.0.0.1:4222 ...")

    try:
        await nc.connect("nats://127.0.0.1:4222", connect_timeout=2)
        print("SUCCESS: Connected to NATS!")
        await nc.close()
    except Exception as e:
        print("FAILED to connect to NATS")
        print("Error:", e)

asyncio.run(test())
