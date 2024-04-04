import threading
import subprocess
import concurrent.futures
import time


def stress(stop_flag):
    command = "stress -t 10s --vm 1 --vm-bytes 128M --cpu 5"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    print("Function 2 has finished its process")
    stop_flag.set()

def polling(stop_flag):
    subprocess.run("echo > polling-report.csv", shell=True)
    while not stop_flag.is_set():
        command = "s-tui --csv -t >> polling-report.csv"
        subprocess.run(command, shell=True, capture_output=True, text=True)
        print("Polling is running...")
        time.sleep(1)
    print("Polling has been stopped")
    

def main():
    # Create a threading.Event object
    stop_flag = threading.Event()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start Stress and Polling concurrently
        thread2 = threading.Thread(target=stress, args=(stop_flag,))
        thread3 = threading.Thread(target=polling, args=(stop_flag,))


    # Start both threads
    start_time = time.time()
    print("Start time:",start_time)
    thread2.start()
    thread3.start()

    # Wait for Stress to finish
    thread2.join()

    # Set the flag to indicate that all processes are complete
    stop_flag.set()

    # Wait for Polling to finish
    thread3.join()

    end_time = time.time()
    print("End time:",end_time)

    print("All functions have completed")

if __name__ == "__main__":
    main()
