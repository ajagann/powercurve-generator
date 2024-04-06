from polling_base import Polling
import logging
import time
import pyRAPL
import os
import multiprocessing as mp

# pyRAPL.setup(devices=[pyRAPL.Device.PKG]) 

# csv_output = pyRAPL.outputs.CSVOutput('polling-results.csv')
# @pyRAPL.measureit(output=csv_output)   

class RAPLPolling(Polling):

    def run(self, queue: mp.Queue, stop_event: mp.Event):
        start_time = time.time()

        while not stop_event.is_set():
            observed_power = 100
            end_time = time.time()
            queue.put((start_time, end_time, observed_power, 'watts'))
            # Wait every 1 second
            time.sleep(1)

        # meter = pyRAPL.Measurement(label='polling')
        # meter.begin()
        # while True:
        #     time.sleep(1)
        
        # meter.end()


        # for _ in range(5):  # number of process
        #     meter = pyRAPL.Measurement(label='polling')
        #     meter.begin()

        #     utilization, frequency = self.run_get_cpu()
            
        #     meter.end()
        #     data_points.append((utilization, frequency))
        #     time.sleep(1)
        #     # print(data_points)

if __name__ == "__main__":
    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.INFO)


#     # Get the pipe from cmd-line args
#     pipe_r = int(os.argv[1])
#     pipe_w = int(os.argv[2])
    
#     logging.basicConfig()
#     # todo add command line arguments using:
#     #   https://docs.python.org/3/library/argparse.html
#     #   set level to debug only if -debug is used
#     logging.getLogger().setLevel(logging.DEBUG)

#     poll = RAPLPolling()
#     poll.run_polling()

#     csv_output.save()
