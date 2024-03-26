import multiprocessing as mp
import subprocess as sp
import threading as th
from time import sleep

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



class Benchmark:
    def run(self, event):
        # running the benchmark
        # probably a wrapper around: sp.CompletedProcess = sp.run("args_of_some_sort")
        # set the event to signal that the benchmark has finished
        event.set()
    
    def calibrate(self):
        # To be defined in the child class
        pass


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
                print(f"Current CPU usage: {cpu_percent}%")
                if cpu_percent >= cpu_threshold:
                    print("CPU usage reached threshold. Stopping requests.")
                    return

        global stop_event
        stop_event = threading.Event() # Create stop event

        # Start monitoring CPU usage in a separate thread
        cpu_monitor_thread = concurrent.futures.ThreadPoolExecutor().submit(monitor_cpu_usage)

        # Create a thread pool executor to maximize CPU usage
        while not cpu_monitor_thread.done():
            print(f"Issuing {num_requests} requests...")

            # Issue multiple requests concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(send_request, url) for _ in range(num_requests)]

                # Wait for all requests to complete or CPU usage threshold is reached
                for future in concurrent.futures.as_completed(futures):
                    if cpu_monitor_thread.done():
                        break
                    status_code = future.result()
                    if status_code is not None:
                        print(f"Request completed with status code: {status_code}")
            
            print("Increasing number of requests...")
            num_requests += 100
        
        # Signal the threads to stop
        print("Signaling threads to stop...")
        stop_event.set()

        return num_requests

    def poll(self, throughput):
        pass

if __name__ == "__main__":
    # chip = GreenChips('NGINX', 200)
    # chip.run()

    nb = NGINXBench()
    nb.calibrate()