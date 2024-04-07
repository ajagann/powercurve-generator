from polling_base import Polling
import logging
import time
import pyRAPL
import os
import multiprocessing as mp

class RAPLPolling(Polling):
    def __init__(self) -> None:
        pyRAPL.setup(devices=[pyRAPL.Device.PKG])
        self._measurement = pyRAPL.Measurement("package")

    def run(self, queue: mp.Queue, stop_event: mp.Event):
        # Observe power value for package (all sockets) every 1 second
        while not stop_event.is_set():
            self._measurement.begin()
            time.sleep(1)
            self._measurement.end()

            result = self._measurement.result
            duration = result.duration
            start = result.timestamp
            end = result.timestamp + duration
            observed_energy_microjoules = result.pkg
            
            # To get to power in watts, convert microjoules to joules
            # (multiply by 1e-6) then divide by duration of measurement
            observed_power = []
            if type(observed_energy_microjoules) == list:
                for e in observed_energy_microjoules:
                    observed_power.append(e * 1e-6/duration)
            else:
                observed_power.append(observed_energy_microjoules * 1e-6/duration)
                
            queue.put((start, end, observed_power, 'W'))
            # Wait every 1 second
            time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig()
    # todo add command line arguments using:
    #   https://docs.python.org/3/library/argparse.html
    #   set level to debug only if -debug is used
    logging.getLogger().setLevel(logging.INFO)
