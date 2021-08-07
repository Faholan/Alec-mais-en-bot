"""Adapted from Jishaku."""


import asyncio
import os
import re
import subprocess
import time

SHELL = os.getenv("SHELL") or "/bin/bash"


def background_reader(stream, loop: asyncio.AbstractEventLoop, callback):
    """
    Reads a stream and forwards each line to an async callback.
    """

    for line in iter(stream.readline, b''):
        loop.call_soon_threadsafe(loop.create_task, callback(line))


class ShellReader:
    """Passively reads from a shell and buffers results for read."""

    def __init__(self, code: str, timeout: int = 120, loop: asyncio.AbstractEventLoop = None):
        sequence = [SHELL, '-c', code]
        self.ps1 = "$"
        self.highlight = "sh"

        self.process = subprocess.Popen(
            sequence,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.close_code = None

        self.loop = loop or asyncio.get_event_loop()
        self.timeout = timeout

        self.stdout_task = self.make_reader_task(
            self.process.stdout,
            self.stdout_handler,
        )
        self.stderr_task = self.make_reader_task(
            self.process.stderr,
            self.stderr_handler,
        )

        self.queue = asyncio.Queue(maxsize=250)

    @property
    def closed(self):
        """Check if both tasks are done."""
        return self.stdout_task.done() and self.stderr_task.done()

    async def executor_wrapper(self, *args, **kwargs):
        """Call wrapper for stream reader."""
        return await self.loop.run_in_executor(None, *args, **kwargs)

    def make_reader_task(self, stream, callback):
        """Create a reader executor task for a stream."""
        return self.loop.create_task(
            self.executor_wrapper(
                background_reader,
                stream,
                self.loop,
                callback,
            ),
        )

    @staticmethod
    def clean_bytes(line):
        """Clean a byte sequence of shell directives and decode it."""
        text = line.decode("utf-8").replace("\r", "").strip("\n")
        return re.sub(r"\x1b[^m]*m", "", text).replace("``", "`\u200b`").strip("\n")

    async def stdout_handler(self, line):
        """Handle stdout."""
        await self.queue.put(self.clean_bytes(line))

    async def stderr_handler(self, line):
        """Handle stderr."""
        await self.queue.put(self.clean_bytes(b"[stderr] " + line))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.process.kill()
        self.process.terminate()
        self.close_code = self.process.wait(timeout=0.5)

    def __aiter__(self):
        return self

    async def __anext__(self):
        last_output = time.perf_counter()

        while not self.closed or not self.queue.empty():
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1)
            except asyncio.TimeoutError as exception:
                if time.perf_counter() - last_output >= self.timeout:
                    raise exception
            else:
                last_output = time.perf_counter()
                return item

        raise StopAsyncIteration()
