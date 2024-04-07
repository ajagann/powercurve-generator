import logging
# from ..green_chips.benchmark_base import Benchmark
from benchmark_base import Benchmark

import psutil
import requests
import concurrent.futures
import threading
import multiprocessing as mp
from datetime import datetime
from bs4 import BeautifulSoup
import signal
import sys
import os
import numpy as np


"""
    Runs NGINX 3 times to find # requests that utilizes all CPU resources available
    Polls psutil to find 100% utilization
    Returns the throughput value associated with 100% utilization
"""
class NGINXBench(Benchmark):
    def __init__(self):
        self._max_throughput = -1

    def matmult(self, matrix_size, num_matrices):
        matrices = [np.random.rand(matrix_size)]

    def find_optimal_flops(self, max_flops):
        matrix_sizes = [100, 200, 300, 400, 500]  # You can adjust this list to include more matrix sizes
        flops = []

        for matrix_size in matrix_sizes:
            elapsed_time = benchmark(matrix_size)
            num_flops = matrix_size ** 3 * 2  # Number of FLOPs in matrix multiplication
            flops.append((num_flops, elapsed_time))

        # Find the optimal number of FLOPs that maximize CPU resources
        optimal_flops = None
        max_utilization = 0
        for num_flops, elapsed_time in flops:
            utilization = psutil.cpu_percent(interval=1)
            if utilization > max_utilization and num_flops <= max_flops:
                optimal_flops = num_flops
                max_utilization = utilization

        return optimal_flops

    def find_max_throughput(self, initial_num_requests=None, url="http://localhost:80", cpu_threshold=0.5) -> int:
        num_requests = 10000 if initial_num_requests is None else initial_num_requests        
        num_req_increase = 0

        # Start a session
        session = requests.Session()

        def monitor_cpu_usage():
            while True:
                cpu_percent = psutil.cpu_percent(interval=1)
                logging.info(f"Current CPU usage: {cpu_percent}%")
                
                if cpu_percent >= cpu_threshold:
                    logging.info(f"CPU usage reached {cpu_percent}%. Stopping requests.")
                    return

        # Start monitoring CPU usage in a separate thread
        cpu_monitor_thread = concurrent.futures.ThreadPoolExecutor().submit(monitor_cpu_usage)

        # Create a thread pool executor to maximize CPU usage
        start = True
        while not cpu_monitor_thread.done():            
            if not start:
                num_req_increase += num_requests * (1 - psutil.cpu_percent()/100)
                num_requests += num_req_increase
                logging.info(f"Increasing number of requests to {num_requests}")
            else:
                logging.info(f"Issuing {num_requests} requests...")
                start = False

            # Issue multiple requests concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
                futures = [executor.submit(self.send_request, session, url) for _ in range(num_requests)]

                # Wait for all requests to complete or CPU usage threshold is reached
                for future in concurrent.futures.as_completed(futures):
                    if cpu_monitor_thread.done():
                        break
                    status_code = future.result()
                    if status_code != 200:
                        logging.info(f"Request completed with status code: {status_code}")

                logging.info("CPU condition reached. Stopping all threads.")                
                for future in futures:
                    if not future.done():
                        future.cancel()

        return num_requests

    """
        Calibrate - find the amount of work that needs to be done to utilize all CPU resources
    """
    def calibrate(self, num_iterations=1):
        max_throughput = []

        for i in range(num_iterations):
            logging.info(f"Calibration {i+1}/{num_iterations}")
            if len(max_throughput) == 0:
                max_throughput.append(self.find_max_throughput())
                continue
            max_throughput.append(self.find_max_throughput(max_throughput[0]))
        
        self._max_throughput = sum(max_throughput)/len(max_throughput)
        return self._max_throughput

    def run_throughput(self, throughput, url="http://localhost:80"):
        session = requests.Session()
        # Issue multiple requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = [executor.submit(self.send_request, session, url) for _ in range(throughput)]

            # Wait for all requests to complete or CPU usage threshold is reached
            for future in concurrent.futures.as_completed(futures):
                status_code = future.result()
                if status_code != 200:
                    logging.info(f"Request completed with status code: {status_code}")

    def run(self, queue: mp.Queue):
        logging.info("Starting benchmark")

        util_steps = [i/10 for i in range(11)]
        util_throughputs = [(step, int(self._max_throughput * step)) for step in util_steps]
        
        for util_step, throughput in (util_throughputs[:1]):
            logging.info(f"Benchmarking {util_step}%")
            
            start = str(datetime.now())
            self.run_throughput(throughput)
            end = str(datetime.now())
            
            queue.put((start, end, throughput, util_step))
        
        logging.info(f"Benchmarking completed")

if __name__ == "__main__":
    # logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)-5.5s]  %(message)s")
    logFormatter = logging.Formatter("[%(levelname)-5.5s] [%(threadName)s] \t %(message)s")
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.INFO)
