#!venv/bin/python

import psutil
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas
import re
import subprocess

def benchmark1():
    st.header("CPU Benchmark with Py PSUTIL")

    def get_cpu_data():
        return psutil.cpu_percent(), psutil.cpu_freq().current

    def plot_power_curve(data_points):
        utilizations, frequencies = zip(*data_points)
        plt.figure()
        plt.plot(utilizations, frequencies)
        plt.xlabel('CPU Utilization (%)')
        plt.ylabel('CPU Frequency (MHz)')
        plt.title('CPU Power Curve')
        plt.grid(True)
        st.pyplot(plt)

    data_points = []
    for _ in range(100):
        utilization, frequency = get_cpu_data()
        data_points.append((utilization, frequency))
        st.write(f"Utilization: {utilization}%, Frequency: {frequency} MHz")
        st.progress(utilization / 100)  # Show progress bar based on utilization
        st.empty()  # Add some space between each update
        st.text("Collecting data...")
        time.sleep(1)  # Sleep for 1 second


    st.success("Data collection complete!")
    st.subheader("Power Curve")
    plot_power_curve(data_points)


def benchmark2():

    st.title("CPU Benchmark with NGINX")

    # Function to run wrk and parse the output
    def run_wrk(url, duration=10, connections=10):
        command = f"wrk -t1 -c{connections} -d{duration}s {url}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout
        match = re.search(r"Requests/sec:\s+([0-9.]+)", output)
        if match:
            requests_per_sec = float(match.group(1))
        else:
            requests_per_sec = None
        return requests_per_sec

    # Input form for user to enter NGINX URL
    nginx_url = st.text_input("Enter NGINX URL", "http://localhost:8080")

    # Run the benchmark when the user clicks the button
    if st.button("Run Benchmark", on_click=st.session_state.clear):
        st.text("Running benchmark...")
        requests_per_sec = run_wrk(nginx_url)
        if requests_per_sec is not None:
            st.success(f"Requests per second: {requests_per_sec}")
        else:
            st.error("Failed to get benchmark result")
