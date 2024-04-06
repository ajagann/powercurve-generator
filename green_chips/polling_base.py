from abc import ABC, abstractmethod
import multiprocessing as mp

class Polling(ABC):
    @abstractmethod
    def run(self, queue: mp.Queue, stop_event: mp.Event):
        pass
