#!/usr/bin/env python3

import sys, os
import subprocess
## NOTE: Library for heat map generation
import plotly.graph_objects as go

from utils.constants import *
from utils.math_utils import *

sys.path.append(os.pardir)
sys.path.append(".")

def get_heatmap_figure(x_value, y_values, z_values):
    figure_heatmap = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_value,
        y=y_values))
    return figure_heatmap

def visualize_io_pattern(source_file_name, logs_kind):

    # NOTE: Heatmap's data
    heatmap_time_values = []
    heatmap_latency_values = []
    heatmap_bytes_values = []
    heatmap_pid_values = []

    minimal_required_amount_of_data = 7

    iosnoop_logs_file = open(source_file_name)
    current_line = iosnoop_logs_file.readline()

    while (current_line):
        polling_data_values = current_line.split()

        if (len(polling_data_values) < minimal_required_amount_of_data):
            # NOTE: Preventing parsing a single PID (sometimes, the polling ...
            # ... captures this kind of output.
            current_line = iosnoop_logs_file.readline()
            continue
        # TODO: Replace hard-coded index with string pattern (?)

        captured_time = polling_data_values[0]
        if (not is_numberic_value(captured_time)):
            current_line = iosnoop_logs_file.readline()
            continue

        heatmap_time_values.append(polling_data_values[IOSNOOP_PARSING.TIME_VALUE_INDEX])
        heatmap_pid_values.append(polling_data_values[IOSNOOP_PARSING.PID_VALUE_INDEX])
        heatmap_bytes_values.append(polling_data_values[IOSNOOP_PARSING.BYTES_VALUE_INDEX])
        heatmap_latency_values.append(polling_data_values[IOSNOOP_PARSING.LATENCY_VALUE_INDEX])
        current_line = iosnoop_logs_file.readline()

    # NOTE: Creating the heat map
    heatmap_x_values = heatmap_time_values
    heatmap_y_values = heatmap_latency_values
    heatmap_z_values = heatmap_bytes_values
    heatmap_z_labels = [heatmap_bytes_values]

    hovertext = list()
    print("Launch map drawing..")
    # io_pattern_heat_map = go.Figure(data=go.Heatmap(
    #     z=heatmap_z_values,
    #     x=heatmap_x_values,
    #     y=heatmap_y_values,
    #     hoverinfo='text',
    #     text=hovertext))
    latency_heatmap = get_heatmap_figure(heatmap_x_values, heatmap_y_values, heatmap_z_values)
    heatmap_shared_title = f'iosnoop statistics for {logs_kind}'
    latency_heatmap.update_layout(
        title=heatmap_shared_title,
        yaxis_nticks=40,
        xaxis_title="Time, s",
        yaxis_title="Latency, ms")

    bytes_heatmap = get_heatmap_figure(heatmap_x_values, heatmap_z_values, heatmap_y_values)
    bytes_heatmap.update_layout(
        title=heatmap_shared_title,
        xaxis_title="Time, s",
        xaxis_nticks=40,
        yaxis_title="Bytes")


    print("Exporting heatmap into file..")
    try:
        latency_heatmap.write_html(file="latency_heatmap.html", auto_open=False)
        bytes_heatmap.write_html(file="bytes_heatmap.html", auto_open=False)

        # latency_heatmap.write_image("latency_heatmap.svg")
        # bytes_heatmap.write_image("bytes_heatmap.svg")
    except Exception as e:
        print(e)
        sys.exit(-1)

def visualize_io_pattern_with_captured_values(bcc_tools_location, amount_of_logs_to_collect):

    biosnoop_process = subprocess.Popen(['python {biosnoop_script_location}'.format(biosnoop_script_location=bcc_tools_location)],
                                        shell=True, stdout=subprocess.PIPE)
    # NOTE: Heatmap's data
    heatmap_time_values = []
    heatmap_latency_values = []
    heatmap_bytes_values = []
    heatmap_pid_values = []

    minimal_required_amount_of_data = 5

    while (len(heatmap_time_values) < amount_of_logs_to_collect):
        polling_result = biosnoop_process.stdout

        polling_data_values = polling_result.readline().decode("utf-8").split()

        if (len(polling_data_values) < minimal_required_amount_of_data):
            # NOTE: Preventing parsing a single PID (sometimes, the polling ...
            # ... captures this kind of output.
            continue
        # TODO: Replace hard-coded index with string pattern (?)

        heatmap_time_values.append(polling_data_values[IOSNOOP_PARSING.TIME_VALUE_INDEX])
        heatmap_pid_values.append(polling_data_values[IOSNOOP_PARSING.PID_VALUE_INDEX])
        heatmap_bytes_values.append(polling_data_values[IOSNOOP_PARSING.BYTES_VALUE_INDEX])
        heatmap_latency_values.append(polling_data_values[IOSNOOP_PARSING.LATENCY_VAUE_INDEX])
        # time.sleep(0.2)

    # NOTE: Creating the heat map
    heatmap_x_values = heatmap_time_values
    heatmap_y_values = heatmap_latency_values
    # TODO: Parse bytes values into the buckets
    heatmap_z_values = heatmap_bytes_values
    heatmap_z_labels = [heatmap_bytes_values]

    hovertext = list()
    for yi, yy in enumerate(heatmap_y_values):
        hovertext.append(list())
        # NOTE: Getting the process name by its ID
        print(f"heatmap_pid_values[yi]: {heatmap_pid_values[yi]}")
        process_name_fetch_result_raw = subprocess.run(
            ['ps -p {proc_id} -o comm='.format(proc_id=heatmap_pid_values[yi])], shell=True, stdout=subprocess.PIPE)
        process_name_fetch_result = process_name_fetch_result_raw.stdout.decode("utf-8").split()
        residentSetSize = "unknown"
        processName = "unknown"
        cpu = "unknown"
        virtualMemorySize = "unknown"
        ps_cmd_raw_result = []
        print(f"process_name_fetch_result: {process_name_fetch_result}")
        target_process_name = ""
        if (len(process_name_fetch_result) > 0):
            if (process_name_fetch_result[0] != "PID"):
                target_process_name = process_name_fetch_result[0]
                ps_cmd_result = subprocess.run(
                    ['ps aux | grep {process_name}'.format(process_name=target_process_name)],
                    shell=True,
                    stdout=subprocess.PIPE)
                ps_cmd_raw_result = ps_cmd_result.stdout.decode("utf-8").split()
        else:
            target_process_name = "unknown"

        if (len(ps_cmd_raw_result) > 0):
            # NOTE: Retrieving the info about the process
            ps_cmd_result = subprocess.run(
                ['ps aux | grep {process_name}'.format(process_name=target_process_name)], shell=True,
                stdout=subprocess.PIPE)
            ps_cmd_raw_result = ps_cmd_result.stdout.decode("utf-8").split()
            if (len(ps_cmd_raw_result) == 0):
                continue
            # @param residentSetSize - RSS is the Resident Set Size and is used to show how much memory is allocated to that process and is in RAM.
            # It does not include memory that is swapped out.
            # It does include memory from shared libraries as long as the pages from those libraries are actually in memory.
            # It does include all stack and heap memory.
            residentSetSize = ps_cmd_raw_result[5]

            # @param virtualMemorySize - VSZ is the Virtual Memory Size. It includes all memory that the process can access, ..
            # ...including memory that is swapped out, memory that is allocated, but not used, and ..
            # ... memory that is from shared libraries.
            virtualMemorySize = ps_cmd_raw_result[4]

            cpu = ps_cmd_raw_result[2]
            processName = ps_cmd_raw_result[0]

        for xi, xx in enumerate(heatmap_x_values):
            hovertext[-1].append(
                'Process name: {} <br />Time: {}<br />Latency: {}<br />Bytes: {} <br /> PID: {}, CPU: {} <br /> Virtual Memory Size: {} <br /> Resident Set Size: {}'.format(
                    target_process_name, xx, yy, heatmap_z_labels[0][yi], heatmap_pid_values[yi], cpu,
                    virtualMemorySize, residentSetSize))

    io_pattern_heat_map = go.Figure(data=go.Heatmap(
        z=heatmap_z_values,
        x=heatmap_x_values,
        y=heatmap_y_values,
        hoverinfo='text',
        text=hovertext))

    io_pattern_heat_map.update_layout(
        title='BIOSNOOP statistics',
        xaxis_nticks=10,
        xaxis_title="Time, s",
        yaxis_title="Latency, ms")

    io_pattern_heat_map.show()
