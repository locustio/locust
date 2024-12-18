import asyncio

import aiohttp


class AIOUser:
    tasks = []

    def run(self) -> None:
        self._running = True
        self._task: asyncio.Task = asyncio.create_task(self._run_tasks())

    async def _run_tasks(self) -> None:
        try:
            while self._running:
                for t in self.tasks:
                    await t(self)
        except asyncio.CancelledError:
            print("cancelled")
        finally:
            print("stopped")

    async def stop(self) -> None:
        self._running = False
        self._task.cancel()


class AIOHttpUser(AIOUser):
    def __init__(self) -> None:
        self.client = aiohttp.ClientSession()

    async def stop(self) -> None:
        await super().stop()
        await self.client.close()


class MyUser(AIOHttpUser):
    async def task_1(self) -> None:
        resp = await self.client.get("https://www.locust.cloud")
        print(resp)

    async def task_2(self) -> None:
        print(await self.client.get("https://www.google.com"))

    tasks = [task_1, task_2]


async def main() -> None:
    a = MyUser()
    b = MyUser()
    a.run()
    b.run()
    await asyncio.sleep(5)
    await a.stop()
    await b.stop()


asyncio.run(main())
