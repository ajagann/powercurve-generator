import pyRAPL
import subprocess, sys
from subprocess import Popen, PIPE, STDOUT
import warnings
import requests
import time


pyRAPL.setup()

#output
csv_output = pyRAPL.outputs.CSVOutput('results_cpu_polling-v6.csv')
@pyRAPL.measureit(output=csv_output)

def nginx():
    # url = "http://localhost:8080/benchmark/"
    url = "http://192.168.15.20/auth/login/?next=/"

    with pyRAPL.Measurement('nginx'):
        # Run your CPU-intensive code here
        for i in range(5): 
            response = requests.get(url)
            time.sleep(2)  # Polling interval in seconds
            if response.status_code == 200:
                print("NGINX is serving the request.")
            else:
                print("no http response")
            pass    

# def stress():
#     # example w stress
#     result = subprocess.Popen(['stress', '-t', '10s', '--vm', '1', '--vm-bytes', '128M', '--cpu', '5'], stdout=PIPE)
#     result.communicate()[0]
#     output = result.stdout


def polling_time():
    # Get the current time
    start_time = time.time()
    print("Start time:",start_time)

    # Add Benchmarking function here
    nginx()
    # stress()

    # Calculate the elapsed time
    end_time = time.time()
    print("End time:",end_time)

    elapsed_time = end_time - start_time

    # Return the elapsed time
    return elapsed_time

# Call the function and print the elapsed time
# print("Elapsed time:", )

if __name__ == "__main__":
    polling_time()

csv_output.save()
