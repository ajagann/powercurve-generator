import multiprocessing as mp
import subprocess as sp
import logging

class GreenChips:

    def __init__(self, benchmark_type: str, is_calibrate: bool, polling: str, tdp: int | None = None):
        self._benchmark_type = benchmark_type
        self._polling = polling
        self._tdp = tdp
        self._is_calibrate = is_calibrate
        self._supported_benchmarks = {"NGINX": "nginx_bench.py"}
        self._bench_args = []
        self._poll_args = []

    def create_bench_args(self):
        # add python as a running program if it is a python script
        if self._supported_benchmarks[self._benchmark_type].split('.')[1] == 'py':
            self._bench_args.append("python")
        # add benchmark file to run
        self._bench_args.append(self._supported_benchmarks[self._benchmark_type])
        # add the rest of the args
        self._bench_args.append("other relevant args")

    def create_poll_args(self):
        # add python as a running program if it is a python script
        if self._polling.split('.')[1] == 'py':
            self._poll_args.append("python")
        # add polling file to run
        self._poll_args.append(self._polling)
        # add the rest of the args
        self._poll_args.append("other relevant args")


    def run(self):
        # parse args for subprocesses
        self.create_bench_args()
        self.create_poll_args()

        # create processes for benchmark
        benchmark_proc = sp.Popen(self._bench_args, stdout=sp.PIPE, stdin=sp.PIPE)
        max_throughput = 0

        # perform this only if there is a separate calibration function in benchmark
        if self._is_calibrate:
            max_throughput = benchmark_proc.stdout.readline().decode().strip()
            # send acknowledgement to benchmark
            benchmark_proc.stdin.write(b"continue\n")
            benchmark_proc.stdin.flush()

        # create processes for polling
        polling_proc = sp.Popen(self._poll_args, stdout=sp.PIPE,  stdin=sp.PIPE)

        # get output from benchmarking
        benchmark_results = benchmark_proc.stdout.readline().decode().strip()

        # wait for the benchmark to finish
        benchmark_proc.wait()

        # send a message to polling to stop
        if polling_proc.poll() is None:
            # polling_proc.communicate(input=b"stop") # another approach
            polling_proc.stdin.write(b"stop\n")
            polling_proc.stdin.flush()

        # get output from polling
        polling_results = polling_proc.stdout.readline().decode().strip()

        # wait for the polling to finish
        polling_proc.wait()

        # result analysis happens here
        # make a class that parses and manipulates the data as needed
        # make a class that takes all the output we got and puts it in a CSV

        """
        # Something like this happens in benchmark:
        # send output from calibrate() to the main process
        print(max_throughput)
        sys.stdout.flush()

        # wait for acknowledgement from green_chips
        while True:
            line = input().strip()
            if line == "continue":
                break
        
        # execute benchmarking
        print(benchmark_results)
        sys.stdout.flush()
        """

if __name__ == "__main__":

    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.DEBUG)
    chip = GreenChips(benchmark_type='NGINX', is_calibrate=True, polling='polling.py', tdp=200)
    chip.run()