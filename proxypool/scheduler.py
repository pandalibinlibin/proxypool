import time
import multiprocessing
import asyncio
from subprocess import run as subprocess_run
from pathlib import Path


class Scheduler:
    def __init__(self):
        # Initialize the processes
        self.getter_process = None
        self.tester_process = None

    def start_getter(self):
        """Start the getter process to run every 60 seconds."""
        while True:
            try:
                # Run getter.py as a subprocess
                subprocess_run(["python", str(Path("getter.py"))])
            except Exception as e:
                print(f"Error running getter.py: {e}")
            time.sleep(60)

    async def _run_tester_async(self):
        """Run tester.py asynchronously."""
        try:
            # Use asyncio to run tester.py
            process = await asyncio.create_subprocess_exec("python", "tester.py")
            await process.wait()
        except Exception as e:
            print(f"Error running tester.py: {e}")

    def start_tester(self):
        """Start the tester process to run every 60 seconds with async execution."""
        while True:
            asyncio.run(self._run_tester_async())
            time.sleep(60)

    def run(self):
        """Start both getter and tester processes."""
        self.getter_process = multiprocessing.Process(target=self.start_getter)
        self.tester_process = multiprocessing.Process(target=self.start_tester)

        self.getter_process.start()
        self.tester_process.start()

        try:
            self.getter_process.join()
            self.tester_process.join()
        except KeyboardInterrupt:
            self.getter_process.terminate()
            self.tester_process.terminate()


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.run()
