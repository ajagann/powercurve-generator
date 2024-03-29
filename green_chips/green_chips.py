import multiprocessing as mp
import subprocess as sp
import logging

class GreenChips:

    def __init__(self, benchmark_type: str, polling: str, tdp: int | None = None):
        self._benchmark_type = benchmark_type
        self._polling = polling
        self._tdp = tdp
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

        # create processes for both methods
        benchmark_proc = sp.Popen(self._bench_args)
        polling_proc =  sp.Popen(self._poll_args)

        # wait for the benchmark to finish
        benchmark_proc.wait()

        # send a message to polling to stop
        if polling_proc.poll() is None:
            polling_proc.communicate(input=b"stop")  # send a stop message

        # where should result analysis happen?

if __name__ == "__main__":

    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.DEBUG)
    chip = GreenChips(benchmark_type='NGINX', polling='polling.py', tdp=200)
    chip.run()