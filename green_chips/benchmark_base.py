from abc import ABC, abstractmethod
import multiprocessing as mp

class Benchmark(ABC):
    @abstractmethod
    def run(self, queue: mp.Queue):
        pass

    @abstractmethod
    def calibrate(self):
        """
        If the benchmark does not need a calibrate, 
        leave function definition empty.
        """
        pass
