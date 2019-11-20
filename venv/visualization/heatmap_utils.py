#!/usr/bin/env python3

import sys, os
import re
import subprocess
## NOTE: Library for heat map generation
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.constants import *
from utils.math_utils import *

sys.path.append(os.pardir)
sys.path.append(".")

def get_heatmap_figure(x_value, y_values, z_values):
    hovertext = get_hover_text_labels(x_value, y_values)
    figure_heatmap = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_value,
        y=y_values,
        text=hovertext))
    return figure_heatmap

def get_hover_text_labels(x_values, y_values):
    hovertext = list()
    for yi, yy in enumerate(y_values):
        hovertext.append(list())
        for xi, xx in enumerate(x_values):
            hovertext[-1].append('Process name: test')
    return hovertext

def get_core_charts_from_file(filename, kind):
    print(f"Parsing file {filename}...")
    # NOTE: Heatmap's data
    heatmap_time_values = []
    heatmap_latency_values = []
    heatmap_bytes_values = []
    heatmap_pid_values = []

    minimal_required_amount_of_data = 7
    iosnoop_logs_file = open(filename)
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

    latency_heatmap = get_heatmap_figure(heatmap_x_values, heatmap_y_values, heatmap_z_values)
    heatmap_shared_title = f'iosnoop statistics for {kind}'
    latency_heatmap.update_layout(
        title=heatmap_shared_title,
        yaxis_nticks=40,
        xaxis_title="I/O Start time (s)",
        yaxis_title="Latency, ms",
        xaxis_tickformat=".4f")

    bytes_heatmap = get_heatmap_figure(heatmap_x_values, heatmap_z_values, heatmap_y_values)
    bytes_heatmap.update_layout(
        title=heatmap_shared_title,
        xaxis_title="I/O Start time (s)",
        xaxis_nticks=40,
        yaxis_title="Bytes",
        xaxis_tickformat=".4f")

    return [bytes_heatmap, latency_heatmap]

def visualize_io_pattern(source_file_name, logs_kind = ""):
    if not os.path.exists(source_file_name):
        raise Exception("Unable to get visualization data from file {source_file_name} since it doesn't exist.")

    if logs_kind == "":
        # NOTE: Use file name as a default logs find.
        logs_kind = source_file_name

    heatmaps = get_core_charts_from_file(source_file_name, source_file_name)
    result_dashboard_filename = "result.html"
    merge_figures_into_single_html(result_dashboard_filename, heatmaps)

def generete_html_for_figure(figure, html_file_name):
    try:
        figure.write_html(file=html_file_name, auto_open=False)
    except Exception as e:
        print(f"Unable to save figure as an HTML into file {html_file_name}. Details: {e}")
        return ""
    return html_file_name

def merge_figures_into_single_html(result_file_name, figures = []):
    figures_directory_name = "figures"
    if not os.path.exists(figures_directory_name):
        os.mkdir(figures_directory_name)

    result_file_extension = ".html"
    if result_file_name.endswith(result_file_extension):
        result_file_name = result_file_name[:-1*(len(result_file_extension))]
    shared_html_graphs = open(f"{figures_directory_name}/{result_file_name}{result_file_extension}", "w")
    shared_html_graphs.write("<html><head></head><body>" + "\n")
    for index, figure in enumerate(figures):
        tmp_figure_html_filename = f"figure-{index}{result_file_extension}"
        tmp_file_path_with_directory = f"{figures_directory_name}/{tmp_figure_html_filename}"
        figure.write_html(file=tmp_file_path_with_directory, auto_open=False)
        shared_html_graphs.write("  <object data=\"" + tmp_figure_html_filename + "\" width=\"1000\" height=\"500\"></object>" + "\n")
    return result_file_name

def merge_html_files(mering_html_filenames, result_file_name):
    result_file_extension = ".html"

    shared_html_graphs = open(f"{result_file_name}{result_file_extension}", "w")
    shared_html_graphs.write("<html><head></head><body>" + "\n")
    for merging_file in mering_html_filenames:
        if not os.path.exists(merging_file):
            raise Exception(f"Unable to merge {merging_file} since it doesn't exist.")
        shared_html_graphs.write("  <object data=\"" + merging_file + "\" width=\"1000\" height=\"500\"></object>" + "\n")

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
