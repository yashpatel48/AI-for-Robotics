import asyncio
from rosa_agent import agent

async def main():
    print("ROSA Agent ready. Type a question.")

    while True:
        user_input = input("> ")

        result = await agent.run(user_input)

        # Print ONLY the assistant-visible output
        print(result.data)

asyncio.run(main())
