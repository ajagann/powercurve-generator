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

class NGINXBench(Benchmark):
    """
        Runs NGINX 3 times to find # requests that utilizes all CPU resources available
        Polls psutil to find 100% utilization
        Returns the throughput value associated with 100% utilization
    """
    def cpu_bound_task(self, x):
        pr = 201234
        for _ in range(10**7):
            pr * pr
            pr = pr + len(x)

    def send_request(self, session, url, verify=False):
        try:
            response = session.get(url, verify=False)
            # Do work that represents what will be done in the future
            soup = BeautifulSoup(response.content, features="html.parser")
            res = soup.findAll('a')
            self.cpu_bound_task(res)

            return response.status_code
        except Exception as e:
            return str(e)

    def find_max_throughput(self, initial_num_requests=None, url="http://localhost:80", cpu_threshold=95) -> int:
        num_requests = 1000000 if initial_num_requests is None else initial_num_requests        
        num_req_increase = 0

        # Start a session
        s = requests.Session()

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
                futures = [executor.submit(self.send_request, s, url) for _ in range(num_requests)]

                # Wait for all requests to complete or CPU usage threshold is reached
                # TODO: Fix this such that as threads complete 
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
    
    def calibrate(self, num_iterations=3) -> int:
        max_throughput = []

        for _ in range(num_iterations):
            if len(max_throughput) == 0:
                max_throughput.append(self.find_max_throughput())
                continue
            max_throughput.append(self.find_max_throughput(max_throughput[0]))
        
        return sum(max_throughput)/len(max_throughput)

    def run(self, throughput, url="http://localhost:80"):
        s = requests.Session()
        # Issue multiple requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = [executor.submit(self.send_request, s, url) for _ in range(throughput)]

            # Wait for all requests to complete or CPU usage threshold is reached
            for future in concurrent.futures.as_completed(futures):
                status_code = future.result()
                if status_code != 200:
                    logging.info(f"Request completed with status code: {status_code}")

if __name__ == "__main__":
    # logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)-5.5s]  %(message)s")
    logFormatter = logging.Formatter("[%(levelname)-5.5s] [%(threadName)s] \t %(message)s")
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.INFO)

    # 1. Process - send calibrate val to parent process (Green Chips)
    # 2. Process - Wait for Green Chips to say to start run
    # 3. Run run()
    # 4. Process - Return a list of tuples with (start, end, cpu_util)
    """
    [(start, end, cpu_util), ...]
    """
    #### ALTERNATIVE ####
    # 1. Run calibrate() and run()
    # 2. Send back one piece of info
    #########################

    # Parent process needs to pass connection and event
    # args = sys.argv
    # try:
    #     event, parent_conn = args[1:]
    # except Exception:
    #     logging.error(f"Expecting 2 args, received {len(args - 1)}")

    nb = NGINXBench()
    max_throughput = nb.calibrate(num_iterations=1)
    logging.info(f"Max number of requests {max_throughput}")

    # parent_conn.send(f"{throughput}") # Send data to parent process
    # event.wait()  # Wait for parent process to say that they are ready to begin polling

    ### Do the benchmarking
    logging.info("Starting benchmark")
    util_steps = [i/10 for i in range(11)]
    util_throughputs = [(step, int(max_throughput * step)) for step in util_steps]
    times_to_poll = []
    for util_step, throughput in (util_throughputs):
        logging.info(f"Benchmarking {util_step}%")
        start = str(datetime.now())
        nb.run(throughput)
        end = str(datetime.now())
        times_to_poll.append((start, end, util_step))
    
    logging.info(f"Benchmarking completed")
    # parent_conn.send(times_to_poll)
