from abc import ABC, abstractmethod
import multiprocessing as mp

class Benchmark(ABC):
    @abstractmethod
    def run(self, queue: mp.Queue):
        pass
