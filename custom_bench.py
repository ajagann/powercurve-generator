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
    
    print(f"[matmult_bench({matrix_size})] - {total_flops} - {elapsed_time}s - {flops_per_s}")
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
            print("Threshold met")
            threshold_met_event.set()
    
    print(f"CPU utilization reached {cpu_percent}%")
    return cpu_percent

def find_optimal_work(threshold=95):
    # threshold = os.cpu_count() * 98  # Essentially expecting each logical core to acheive 98% CPU utilization or higher
    stop_event = multiprocessing.Event()
    threshold_met_event = multiprocessing.Event()
    bench_start_event = multiprocessing.Event()
    benchmark_queue = multiprocessing.Queue()

    matrix_size = 1000
    matrix_sizes = []

    cpu_thread=None
    bench_thread=None
    flops_per_s = -1
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
                time.sleep(1)
                if threshold_met_event.is_set():
                    if bench_thread.is_alive():
                        # Target CPU% reached, but benchmark is not done
                        # Decrease amount of work
                        print(f"Decreasing matrix size {matrix_size} -> {matrix_size - 50}")
                        matrix_size -= 50
                        break
                    else:
                        # Matrix size is just right, break out of loop
                        print(f"Found optimal matrix size")
                        optimal_size_found = True
                        break
                else:
                    if bench_thread.is_alive():
                        # Neither the threshold is met nor the work done
                        continue
                    else:
                        # Target CPU% not reached, but benchmark is done
                        # Increase amount of work
                        print(f"Increasing matrix size {matrix_size} -> {matrix_size + 50}")
                        matrix_size += 50
                        break
                    
                # Have a sanity stop
                if matrix_size in matrix_sizes:
                    print(f"Sanity stop")
                    optimal_size_found = True
                    break

            # Signal to cpu_monitor_thread to stop polling CPU
            print(f"Signaling threads to stop")
            stop_event.set()
            if bench_thread.is_alive():
                bench_thread.join()
            if cpu_thread.is_alive():
                cpu_thread.join()

        flops_per_s, elapsed_time = benchmark_queue.get_nowait()
        print(f"Number of FLOPs {flops_per_s} for optimal matrix size {matrix_size}")
    except Exception as e:
        print(f"[ERROR] - {e}")
    finally:
        # Stop all threads
        stop_event.set()
        if cpu_thread and cpu_thread.is_alive():
            cpu_thread.join()
        if bench_thread and bench_thread.is_alive():
            bench_thread.join()

    print(f"Optimal matrix size: {matrix_size}")
    print(f"Optimal FLOPs: {flops_per_s}")
    print(f"Time Elapsed to calculate optimal FLOPs: {elapsed_time}")

    return (matrix_size, flops_per_s)

def calibrate(threshold=95):
    # threshold = os.cpu_count() * 98  # Essentially expecting each logical core to acheive 98% CPU utilization or higher

    optimal_flops = []
    optimal_matrix_sizes = []
    for i in range(3):
        print(f"Calibrate Run {i+1}/3")
        optimal_matrix_size, flops_per_s = find_optimal_work(threshold=threshold)
        optimal_flops.append(flops_per_s)
        optimal_matrix_sizes.append(optimal_matrix_size)

    opt_flops = sum(optimal_flops)/len(optimal_flops)
    opt_size = sum(optimal_matrix_sizes)/len(optimal_matrix_sizes)
    print(f"Optimal Flops {opt_flops} -- {optimal_flops}")
    print(f"Optimal Matrix size {opt_size} -- {optimal_matrix_sizes}")

    return (opt_size, opt_flops)

def run():
    opt_mat_size, opt_flops = calibrate(threshold=98)

    util_steps = [i/10 for i in range(11)]
    util_throughputs = [(step*100, int(opt_mat_size * step)) for step in util_steps]

    res = []
    for util_step, mat_size in util_throughputs:
        print(f"Benchmarking {util_step}% - Matrix size {mat_size} x {mat_size}")
        
        start = str(time.time())
        flops_per_s, _ = matmult_bench(mat_size)
        end = str(time.time())

        res.append((start, end, util_step, flops_per_s, 'FLOPS',))
    
    for i in res:
        print(i)

    return res




run()