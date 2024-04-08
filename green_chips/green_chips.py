import os
import importlib
import inspect
import logging
import multiprocessing as mp
import math
import csv
import platform

# Import GreenChip's abstract classes
from polling_base import Polling
from benchmark_base import Benchmark

class GreenChips:

    # TODO: Add support for args to pass into polling or benchmark
    def __init__(self, benchmark_file: str='nginx_bench.py', polling_file: str='rapl_polling.py', tdp: int=None, csv_output: str=None):
        self._benchmark_file = benchmark_file
        self._benchmark = self._benchmark_file.strip(".py")
        
        self._polling_file = polling_file
        self._polling = self._polling_file.strip(".py")
        
        self._tdp = tdp
        self._supported_benchmarks = {"NGINX": "nginx_bench.py"}

        self._csv_output = 'powercurve.csv' if not csv_output else csv_output

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

        # Launch subprocesses for benchmark and polling
        stop_polling_event = mp.Event()
        polling_proc = mp.Process(target=polling.run, args=(polling_queue, stop_polling_event,))
        benchmark_proc = mp.Process(target=benchmark.run, args=(benchmark_queue,)) # Example expected output of benchmark: [(start, end, throughput, cpu%), ...]

        polling_proc.start()
        benchmark_proc.start()

        # Wait for benchmark to complete, then signal polling process to stop
        # TODO: If something goes wrong with the benchmark, we need to force polling to start
        benchmark_proc.join()
        stop_polling_event.set()
        
        power_curve = self.get_power_curve(benchmark_queue, polling_queue)
        logging.info(f"power_curve =  {power_curve}")

        # TODO: Generate CSV
        logging.info("Generating csv file")
        self.generate_csv(power_curve, self._csv_output)

        logging.info("GreenChips powercurve generation completed")
    
    def generate_csv(self, power_curve, output_file):
        header = ('CPU_perc', 'Throughput_reqPerSec', 'POWER_W')

        with open(output_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerows(power_curve)

    def get_power_time_buckets(self, polling_array):
        time_ticks = []
        for polling_obj in polling_array:
            start_time = float(polling_obj[0])
            end_time = float(polling_obj[1])
            power = sum(polling_obj[2])
            time_ticks.append((start_time, power))     
            time_ticks.append((end_time, -power)) 
        time_ticks.sort(key=lambda x: x[0])
        logging.info(f"time_ticks = {time_ticks}")
        power_time_buckets = []
        curr_total_power = 0
        curr_overlapping_ticks = 0
        for i in range(len(time_ticks) - 1):
            start_tick = time_ticks[i]
            end_tick = time_ticks[i+1]
            start_time = start_tick[0]
            curr_total_power += start_tick[1]
            curr_overlapping_ticks += math.copysign(1, start_tick[1])
            end_time = end_tick[0]
            curr_power = curr_total_power / curr_overlapping_ticks
            power_time_buckets.append((start_time, end_time, curr_power))
        return power_time_buckets
    
    def get_power_for_benchmark_item(self, start_time, end_time, power_time_buckets):
        bucket_index = 0
        left_bucket_index = -1
        # find first bucket index
        while (bucket_index < len(power_time_buckets)):
            if (start_time > power_time_buckets[bucket_index][0]):
                left_bucket_index = bucket_index
                break
            else:
                bucket_index += 1
        if (left_bucket_index == -1):
            # didnt find a bucket, no power was polled for this benchmark data
            return 0
        # find last bucket index
        right_bucket_index = -1
        while (bucket_index < len(power_time_buckets)):
           if (start_time <= power_time_buckets[bucket_index][1]):
                right_bucket_index = bucket_index
                break
           else:
                bucket_index += 1
        if (right_bucket_index == -1):
            # didnt find a bucket, benchmark ended after power stopped polling, last bucket is the best we have
            right_bucket_index =  len(power_time_buckets) - 1
        # get all relevant power values and average them out:
        power_values = []
        for i in range(left_bucket_index, right_bucket_index + 1):
            power_values.append(power_time_buckets[i][2])
        return sum(power_values) / len(power_values)
                   
    def get_power_curve(self, benchmark_queue, polling_queue):
        logging.info(f"merging queues..")
        # TODO not sure we need this sorted
        sorted_benchmark_array = self.get_queue_contents(benchmark_queue)
        polling_array = self.get_queue_contents(polling_queue)
        power_time_buckets_array = self.get_power_time_buckets(polling_array)
        logging.info(f"power_time_buckets_array = {power_time_buckets_array}")
        power_curve = [] # cpu_util, throughput, power
        for benchmark_item in sorted_benchmark_array:
            cpu_util = benchmark_item[2]
            throughput = benchmark_item[3]
            power = self.get_power_for_benchmark_item(float(benchmark_item[0]), float(benchmark_item[1]),power_time_buckets_array)
            power_curve.append((cpu_util, throughput, power))
        return power_curve

    def get_queue_contents(self, queue):
        res = []
        while not queue.empty():
            res.append(queue.get_nowait())
        return res

if __name__ == "__main__":

    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.INFO)

    # TODO get this from cmdline
    benchmark_file = 'matmult_bench.py'
    polling_file = 'rapl_polling.py'

    csv_output = 'powercurve.csv'

    # Run GreenChips
    chip = GreenChips(benchmark_file=benchmark_file, polling_file=polling_file, tdp=200, csv_output=csv_output)
    chip.run()
