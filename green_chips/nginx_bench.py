import logging
from ..green_chips.benchmark_base import Benchmark

import psutil
import requests
import concurrent.futures
import threading


class NGINXBench(Benchmark):
    """
        Runs NGINX 3 times to find # requests that utilizes all CPU resources available
        Polls psutil to find 100% utilization
        Returns the throughput value associated with 100% utilization
    """
    def calibrate(self):
        max_throughput = []

        for _ in range(3):
            if len(max_throughput) < 0:
                max_throughput.append(self.find_max_throughput())
                continue
            max_throughput.append(self.find_max_throughput(max_throughput[0]))
        
        return sum(max_throughput)/len(max_throughput)

    def send_request(self, session, url, verify=False):
        try:
            response = session.get(url, verify=False)
            # Maybe do some work with the response? Write it to a file?
            # CPU bound task
           
            n = 123456
            for _ in range(n):
                n * n

            return response.status_code
        except Exception as e:
            return str(e)

    def find_max_throughput(self, num_requests=None, url="http://localhost:80") -> int:
        if not num_requests:
            num_requests = 1000000  # Number of requests to issue
        cpu_threshold = 95  # CPU usage threshold in percent
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
        while not cpu_monitor_thread.done():
            logging.info(f"Issuing {num_requests} requests...")

            # Issue multiple requests concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.send_request, s, url) for _ in range(num_requests)]

                # Wait for all requests to complete or CPU usage threshold is reached
                for future in concurrent.futures.as_completed(futures):
                    if cpu_monitor_thread.done():
                        break
                    status_code = future.result()
                    if status_code != 200:
                        logging.info(f"Request completed with status code: {status_code}")

            logging.info("Increasing number of requests...")
            num_req_increase += num_requests * (1 - psutil.cpu_percent())
            num_requests += num_req_increase

        return num_requests
    
    def run(self, event, throughput, url = "http://localhost:80"):
        self.send_request(throughput)

        s = requests.Session()
        with concurrent.futures.ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = [executor.submit(self.send_request, s, url) for _ in range(num_requests)]

        event.set()

if __name__ == "__main__":
    nb = NGINXBench()
    # nb.calibrate()
    # nb.run()

    max_num_requests = nb.find_max_throughput()
    logging.info(f"Max number of requests {max_num_requests}")