import asyncio
import aiohttp
import db
from .setting import Setting


class Tester:
    def __init__(self):
        """Initialize the Tester class."""
        self.redis = db.RedisClient()

    async def test_proxy(self, proxy):
        """
        Test a single proxy's availability.

        :param proxy: The proxy to be tested
        """
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                # Convert proxy to the required format
                proxy_url = f"http://{proxy}"
                async with session.get(
                    Setting.TEST_URL, proxy=proxy_url, timeout=15
                ) as response:
                    if response.status == 200:
                        # If test succeeds, set the score to maximum
                        await self.redis.max(proxy)
                    else:
                        # If status code is not 200, decrease the score
                        await self.redis.decrease(proxy)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                # If an error occurs, decrease the score
                await self.redis.decrease(proxy)

    async def run(self):
        """
        Run the proxy testing process.
        """
        print("Starting proxy tester...")
        try:
            proxies = await self.redis.all()
            if proxies:
                tasks = [self.test_proxy(proxy) for proxy in proxies]
                await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Testing error: {e}")


if __name__ == "__main__":
    # Initialize and run the tester
    tester = Tester()
    asyncio.run(tester.run())
