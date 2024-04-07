# Force numpy to run single threaded
import os
os.environ['OMP_NUM_THREADS']="1"
os.environ['OPENBLAS_NUM_THREADS']="1"
os.environ['MKL_NUM_THREADS']="1"
os.environ['VECLIB_MAXIMUM_THREADS']="1"
os.environ['NUMEXPR_NUM_THREADS']="1"

# OMP_NUM_THREADS: openmp,
# OPENBLAS_NUM_THREADS: openblas,
# MKL_NUM_THREADS: mkl,
# VECLIB_MAXIMUM_THREADS: accelerate,
# NUMEXPR_NUM_THREADS: numexpr

import numpy as np
import time
import psutil
import multiprocessing


def matmult_bench(matrix_size, num_matrices=100, start_event=None, stop_early_event=None, queue=None):
    # Wait for cpu_thread to start polling CPU utilization before running benchmark
    if start_event:
        while not start_event.is_set():
            time.sleep(1)

    matrices = [np.random.rand(matrix_size, matrix_size) for _ in range(num_matrices)]
    result = np.eye(matrix_size)
    
    start = time.time()
    for matrix in matrices:
        if stop_early_event and stop_early_event.is_set():
            break
        
        result = np.dot(result, matrix)
    end = time.time()

    total_flops = num_matrices * (2 * matrix_size**3 - matrix_size**2)
    elapsed_time = end - start
    flops_per_s = total_flops/elapsed_time

    if queue:
        try:
            queue.put((flops_per_s, elapsed_time))
        except Exception as e:
            print(f"Error while adding to queue: {e}")
    
    return flops_per_s, elapsed_time


def monitor_cpu_utilization(stop_event, threshold_met_event, threshold=95, process_id=None):
    process = psutil
    if process_id:
        process = psutil.Process(process_id)

    # Calls to psutil should be non-blocking (i.e. do not set an interval)
    cpu_percent = process.cpu_percent()
    while not stop_event.is_set():
        cpu_percent = process.cpu_percent()
        print(f"%CPU - {cpu_percent}")
        time.sleep(1)
        if cpu_percent > threshold:
            threshold_met_event.set()
    
    print(f"CPU utilization reached {cpu_percent}%")
    return cpu_percent


# threshold = os.cpu_count() * 98  # Essentially expecting each logical core to acheive 98% CPU utilization or higher
threshold = 95
stop_event = multiprocessing.Event()
threshold_met_event = multiprocessing.Event()
bench_start_event = multiprocessing.Event()
benchmark_queue = multiprocessing.Queue()

matrix_size = 1000
matrix_sizes = []

cpu_thread=None
bench_thread=None
try:
    optimal_size_found = False
    while not optimal_size_found:
        print(f"Starting loop")
        # Keep track of new matrix size
        matrix_sizes.append(matrix_size)

        print(f"Resetting events")
        # Reset events
        stop_event.clear() 
        threshold_met_event.clear()
        bench_start_event.clear()

        print(f"Starting benchmark thread")
        # start benchmark_thread
        bench_thread = multiprocessing.Process(target=matmult_bench, args=(matrix_size,), kwargs={'start_event': bench_start_event, 'queue': benchmark_queue})
        bench_thread.start()

        # Get PID of bench_thread and start cpu_thread
        # Don't move cpu_thread to before the while loop. We need it to be here b/c
        # we pass in a new bench_id every time
        print(f"Starting cpu monitor thread")
        bench_pid = bench_thread.pid
        cpu_thread = multiprocessing.Process(target=monitor_cpu_utilization, args=(stop_event, threshold_met_event,), kwargs={'threshold': threshold, 'process_id': bench_pid})
        cpu_thread.start()

        # Signal benchmark to start
        bench_start_event.set()

        print(f"Iterating")
        while True:
            """
                0. If benchmark is not complete and threshold is not reached - continue waiting
                1. Benchmark completes and threshold is not reached - increase matrix size
                2. Benchmark does not complete and threshold is reached - decrease matrix size
                3. Benchmark completes and threshold reaches about the same time - optimal matrix size found
                4. If matrix size toggles within 3 iterations - optimal matrix size found 
            """
            if bench_thread.is_alive() and not threshold_met_event.is_set():
                print(f"Increasing matrix size")
                matrix_size += 50
                break
            elif not bench_thread.is_alive() and threshold_met_event.is_set():
                print(f"Decreasing matrix size")
                matrix_size -= 50
                break
            elif not bench_thread.is_alive() and not threshold_met_event.is_set():
                print(f"Optimal matrix size found")
                optimal_size_found = True
                break
            elif len(matrix_sizes) > 3 and matrix_size in matrix_sizes[-3:]:
                print(f"Sort of optimal matrix size found")
                optimal_size_found = True
                break

        # Signal to cpu_monitor_thread to stop polling CPU
        print(f"Signaling threads to stop")
        stop_event.set()
        bench_thread.join()
        cpu_thread.join()

    flops_per_s, elapsed_time = benchmark_queue.get_nowait()
    print(f"Number of FLOPs {flops_per_s} for optimal matrix size {matrix_size} over {elapsed_time} sec")
except Exception as e:
    print(f"[ERROR] - {e}")
finally:
    # Stop all threads
    stop_event.set()
    if cpu_thread:
        cpu_thread.join()
    if bench_thread:
        bench_thread.join()


print(f"Optimal matrix size: {matrix_size}")
print(f"Optimal FLOPs: {flops_per_s}")
print(f"Time Elapsed to calculate optimal FLOPs: {elapsed_time}")