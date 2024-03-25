import pyRAPL
import requests
import time 

pyRAPL.setup()

# output
csv_output = pyRAPL.outputs.CSVOutput('results_cpu_polling-v2.csv')
@pyRAPL.measureit(output=csv_output)

def benchmark():
    # url = "http://localhost:8080/benchmark/"
    url = "http://192.168.15.20/auth/login/?next=/"


    with pyRAPL.Measurement('openstack'):
        # Run your CPU-intensive code here
        for i in range(100): 
            response = requests.get(url)
            time.sleep(2)  # Polling interval in seconds
            if response.status_code == 200:
                print("NGINX is serving the request.")
            else:
                print("no http response")
            pass
        


if __name__ == "__main__":
    benchmark()

csv_output.save()
