from abc import ABC
import threading as th
from time import sleep


class Polling(ABC):
    def run(self, event):
        # running the polling
        thread = th.Thread(target=self.run_polling)
        thread.start()
        # periodically check if the event is set by the benchmark
        while not event.is_set():
            sleep(1)
        thread.join()
        # create output?

    @ABC.abstractmethod
    def run_polling(self):
        pass


