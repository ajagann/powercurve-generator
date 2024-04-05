import psutil
import time
import pyRAPL
import subprocess

pyRAPL.setup(devices=[pyRAPL.Device.PKG])

# subprocess.run("echo > rapl_polling_test.csv", shell=True)
csv_output = pyRAPL.outputs.CSVOutput('rapl_polling_test.csv')
@pyRAPL.measureit(output=csv_output)

def get_cpu_power():
    return psutil.cpu_percent(interval=1), psutil.cpu_freq().current

data_points = []
start_time = time.time()
print("Start time:",start_time)
for _ in range(5):   # number of process
    meter = pyRAPL.Measurement(label='polling')
    meter.begin()
    utilization, frequency = get_cpu_power()
    meter.end()
    data_points.append((utilization, frequency))
    time.sleep(1) 
end_time = time.time()
print("End time:",end_time)    

csv_output.save()