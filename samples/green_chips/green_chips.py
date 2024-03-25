import multiprocessing as mp
import subprocess as sp
import threading as th
from time import sleep

class GreenChips:

    def __init__(self, benchmark_type: str, tdp: int | None = None):
        self._benchmark_type = benchmark_type
        self._tdp = tdp

    def run(self):
        # create event object
        benchmark_finished = multiprocessing.Event()

        # create benchmark and polling classes
        benchmark = Benchmark(self._benchmark_type)
        polling = Polling()

        # set spawn as the start method to ensure reliability across platforms
        mp.set_start_method('spawn')
        # mp.get_context() is a possible alternative if the module is used in a larger program which uses concurrency

        # create processes for both methods
        benchmark_proc = mp.Process(target=benchmark.run, args=(benchmark_finished,))
        polling_proc = mp.Process(target=polling.run, args=(benchmark_finished,))

        # start processes
        benchmark_proc.start()
        polling_proc.start()

        # wait for both processes to finish
        benchmark_proc.join()
        polling_proc.join()



class Benchmark:
    def run(self, event):
        # running the benchmark
        # probably a wrapper around: sp.CompletedProcess = sp.run("args_of_some_sort")
        # set the event to signal that the benchmark has finished
        event.set()

class Polling:
    def run(self, event):
        # running the polling
        thread = th.Thread(target=self.run_polling)
        thread.start()
        # periodically check if the event is set by the benchmark
        while not event.is_set():
            sleep(1)
        thread.join()
        # create output?

    def run_polling(self):
        # probably a wrapper around: sp.run("args_of_some_sort")
        pass


if __name__ == "__main__":
    chip = GreenChips('NGINX', 200)
    chip.run()