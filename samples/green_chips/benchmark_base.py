from abc import ABC


class Benchmark(ABC):
    def run(self, event):
        # running the benchmark
        # probably a wrapper around: sp.CompletedProcess = sp.run("args_of_some_sort")
        # set the event to signal that the benchmark has finished
        event.set()

    @ABC.abstractmethod
    def calibrate(self):
        # To be defined in the child class
        pass
