import asyncio
from tools.search_web_serp import search_web_serp
from dotenv import load_dotenv
import os
load_dotenv()

async def test_serp_tool():
    results = await search_web_serp("Nena-99 Luftballons", max_results=10)
    print(results)

if __name__ == "__main__":
    asyncio.run(test_serp_tool())