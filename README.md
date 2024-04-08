# Green Chips Powercurve Generator

## Requirements
Please install packages in requirements.txt: `pip install -r requirements.txt`

## Limitations
Please note that you will need a Linux distribution to run this code and the system must have a processor that is Sandy Bridge or newer.

## Test it out
To get started, we have coded two benchmarks: `matmult_bench.py` and `nginx_bench.py`
`nginx_bench.py` has some known issues that we are still working through.

Cmdline support will be available soon to pass in parameters, but if you'd like to change which benchmark to run,
please edit line 167 in `green_chips.py`. 

To run generate the powercurve, run `python green_chips/green_chips.py`

## How it works
Here's a diagram of the basic framework. The framework uses the `multiprocessing` library to communicate.

![Powercurve Generator Diagram](documentation/basic_framework.png)

## Adding a new benchmark
If you'd like to write your own benchmark, it's fairly simple to get started. 
1. Create a new class that inherits the `Benchmark` class in `benchmark_base.py`. It is critical that you inherit this class for `green_chip` to run the benchmark.
2. The only function you need to define in the benchmark class is `run()`. You can define whatever classes or functions you need, but `run()` must be defined.
3. The benchmark passes information back to the framework using `multiprocessing.queue`. Add the benchmarking data to the queue to generate the curve.

## Next steps
This is very much a work still in progress. Here is a general list of next steps that will be added as issues in the near future:
* Test in a variety of environments (i.e. containerized envs, different baremetal envs, etc.)
* Look more into how to measure power for applications running on a single socket or across multiple sockets
* Test functionality for hyperthreaded applications
  - May require code changes to accommodate multiple threads
* Add more support for cmdline
* Add support for AMD processors
* Add test cases/CI
* Learn more about power in general to understand more about why we see the results we do
* Make the scripts a bit more dynamic to respond to what information the benchmark is wanting to collect
* Add more structure to the data that is being passed between the Benchmark and GreenChips. It should be more clear what data and in what format the data should be passed.
* Add more documentation/resources about results
* Make framework more robust in general