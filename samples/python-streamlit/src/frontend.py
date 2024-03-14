import json,sys
import streamlit as st
from src.backend import * 

def mainpage():
    st.title("CPU Power Curve generator")
    st.markdown('built to Carbon Hack 24 from Green Software Foundation')

    st.write(" * CPU Info:")
    def get_cpu_info():
        cpu_info = {}
        cpu_info['CPU Count'] = psutil.cpu_count(logical=False) # Physical CPU count
        cpu_info['Total Cores'] = psutil.cpu_count(logical=True) # Total number of CPU cores
        cpu_info['CPU Frequency'] = psutil.cpu_freq().current # Current CPU frequency

        return cpu_info

    cpu_info = get_cpu_info()
    for key, value in cpu_info.items():
        st.write(f'{key}: {value}')

    st.markdown("""---""")

    # Create a sidebar menu
    menu_selection = st.sidebar.radio("Select a Benchmark", ["Py PSUTIL", "NGINX"], index=0)

    # Call the selected function based on the menu selection
    if menu_selection == "Py PSUTIL":
        benchmark1()
    elif menu_selection == "NGINX":
        benchmark2()
