# from polling import Polling
import logging
import psutil
import time
import pyRAPL

pyRAPL.setup(devices=[pyRAPL.Device.PKG]) 
# pyRAPL.setup()

class RAPLPolling():
    csv_output = pyRAPL.outputs.CSVOutput('polling-results.csv')
    @pyRAPL.measureit(output=csv_output)   
    
    def run_get_cpu():
        return psutil.cpu_percent(interval=1, percpu=True), psutil.cpu_freq().current
    
    data_points = []
    start_time = time.time()
    print("Start time:", start_time)

    for _ in range(5):   # number of process
        meter = pyRAPL.Measurement(label='polling')
        meter.begin()

        utilization, frequency = run_get_cpu()

        meter.end()
        data_points.append((utilization, frequency))
        time.sleep(1)

    end_time = time.time()
    print("End time:", end_time)

    csv_output.save()
    
if __name__ == "__main__":
    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.DEBUG)

    poll = RAPLPolling()
