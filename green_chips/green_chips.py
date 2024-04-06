import multiprocessing as mp
import subprocess as sp
import logging
import os
from polling_base import Polling
from benchmark_base import Benchmark
import importlib
import inspect

class GreenChips:

    # TODO: Add support for args to pass into polling or benchmark
    def __init__(self, benchmark_file: str='nginx_bench.py', polling_file: str='rapl_polling.py', tdp: int=None):
        self._benchmark_file = benchmark_file
        self._benchmark = self._benchmark_file.strip(".py")
        
        self._polling_file = polling_file
        self._polling = self._polling_file.strip(".py")
        
        self._tdp = tdp
        self._supported_benchmarks = {"NGINX": "nginx_bench.py"}

    def run(self):
        # Create queues to interact with benchmark and polling processes
        benchmark_queue = mp.Queue()
        polling_queue = mp.Queue()

        # Import the relevant classes
        benchmark_module = importlib.import_module(self._benchmark)
        polling_module = importlib.import_module(self._polling)

        bench_classes = inspect.getmembers(benchmark_module, inspect.isclass)
        poll_classes = inspect.getmembers(polling_module, inspect.isclass)

        logging.info(f"Polling classes: {poll_classes}")

        #TODO: probably fix this so that it's less prone to errors? Is there a better way to do this?
        benchmark = [c for name, c in bench_classes if issubclass(c, Benchmark) and not name=='Benchmark'][0]
        polling = [c for name, c in poll_classes if issubclass(c, Polling) and not name=='Polling'][0]

        # Instantiate classes
        benchmark = benchmark()
        polling = polling()

        # TODO: Put checks here to make sure the classes have all required functions as detailed by the abstract class

        # Run calibrate. TODO: Decide on a format for result, prob tuple (#, metric)
        calibrate_res = benchmark.calibrate()
        logging.info(f"Calibrate result: {calibrate_res}")

        # Launch subprocesses for benchmark and polling
        stop_polling_event = mp.Event()
        polling_proc = mp.Process(target=polling.run, args=(polling_queue, stop_polling_event,))
        benchmark_proc = mp.Process(target=benchmark.run, args=(benchmark_queue,))

        polling_proc.start()
        benchmark_proc.start()

        # Wait for benchmark to complete, then signal polling process to stop
        benchmark_proc.join()
        stop_polling_event.set()
        
        def get_queue_contents(queue):
            res = []
            while not queue.empty():
                res.append(queue.get_nowait())
            return res
        
        logging.info(f"Benchmark queue: {get_queue_contents(benchmark_queue)}")
        logging.info(f"Polling queue: {get_queue_contents(polling_queue)}")

        # TODO: Generate CSV

if __name__ == "__main__":

    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.INFO)

    # TODO get this from cmdline
    benchmark_file = 'nginx_bench.py'
    polling_file = 'rapl_polling.py'

    # Run GreenChips
    chip = GreenChips(benchmark_file=benchmark_file, polling_file=polling_file, tdp=200)
    chip.run()