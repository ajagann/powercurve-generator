import logging
from ..green_chips.benchmark_base import Benchmark


class NGINXBench(Benchmark):
    def run(self, event):
        return super().run(event)

    """
        Runs NGINX 3 times to find # requests that utilizes all CPU resources available
        Polls psutil to find 100% utilization
        Returns the throughput value associated with 100% utilization
    """

    def calibrate(self) -> int:
        import psutil
        import requests
        import concurrent.futures
        import threading

        url = "https://localhost:80"
        num_requests = 100  # Number of requests to issue
        cpu_threshold = 95  # CPU usage threshold in percent

        # Define the function to send HTTP requests
        def send_request(url):
            try:
                response = requests.get(url)
                return response.status_code
            except Exception as e:
                return str(e)

        def monitor_cpu_usage():
            while not stop_event.is_set():
                cpu_percent = psutil.cpu_percent(interval=1)
                logging.info(f"Current CPU usage: {cpu_percent}%")
                if cpu_percent >= cpu_threshold:
                    logging.info("CPU usage reached threshold. Stopping requests.")
                    return

        global stop_event
        stop_event = threading.Event()  # Create stop event

        # Start monitoring CPU usage in a separate thread
        cpu_monitor_thread = concurrent.futures.ThreadPoolExecutor().submit(monitor_cpu_usage)

        # Create a thread pool executor to maximize CPU usage
        while not cpu_monitor_thread.done():
            logging.info(f"Issuing {num_requests} requests...")

            # Issue multiple requests concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(send_request, url) for _ in range(num_requests)]

                # Wait for all requests to complete or CPU usage threshold is reached
                for future in concurrent.futures.as_completed(futures):
                    if cpu_monitor_thread.done():
                        break
                    status_code = future.result()
                    if status_code is not None:
                        logging.info(f"Request completed with status code: {status_code}")

            logging.info("Increasing number of requests...")
            num_requests += 100

        # Signal the threads to stop
        logging.info("Signaling threads to stop...")
        stop_event.set()

        return num_requests

    def poll(self, throughput):
        pass