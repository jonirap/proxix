from threading import Thread
from typing import List

from ..generics import D
from ..server import Server


class ThreadedServer(Server[D]):
    def start(self):
        # type: () -> None
        threads = []  # type: List[Thread]
        for channel in self._get_channels():
            t = Thread(target=channel.listen)
            threads.append(t)
            t.start()
            print("Started thread {}".format(t.name))
        print("Joining {} threads".format(len(threads)))
        for t in threads:
            t.join()
