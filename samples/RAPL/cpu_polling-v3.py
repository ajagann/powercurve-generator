import pyRAPL

pyRAPL.setup()

#output
csv_output = pyRAPL.outputs.CSVOutput('results_cpu_polling-v3.csv')
@pyRAPL.measureit(output=csv_output)

def test(N):
    a = 0
    for i in range(N):
        a += 1
    return a

test(1000000)

csv_output.save()