import pyRAPL
import subprocess

pyRAPL.setup()

#output
csv_output = pyRAPL.outputs.CSVOutput('results_cpu_polling-v4.csv')
@pyRAPL.measureit(output=csv_output)

def rapl_stress():
    command = "stress -t 10s --vm 1 --vm-bytes 128M --cpu 5"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    
for _ in range(5):
	rapl_stress()

csv_output.save()