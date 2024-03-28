import multiprocessing as mp
import subprocess as sp
import logging

from ..green_chips.nginx_bench import NGINXBench
from ..green_chips.polling import Polling


class GreenChips:

    def __init__(self, benchmark_type: str, tdp=None): #| None = None):
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





if __name__ == "__main__":
    # chip = GreenChips('NGINX', 200)
    # chip.run()
    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.DEBUG)
    nb = NGINXBench()
    nb.calibrate()