from abc import ABC

class Benchmark(ABC):
    @ABC.abstractmethod
    def run(self):
        pass

    @ABC.abstractmethod
    def calibrate(self):
        pass

    @ABC.abstractmethod
    def send_signal(self):
        pass