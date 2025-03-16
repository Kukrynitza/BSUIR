from threading import Timer
import asyncio


class Debouncer:
    def __init__(self, delay):
        self.delay = delay
        self.timer = None

    def debounce(self, func):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.delay, func)
        self.timer.start()