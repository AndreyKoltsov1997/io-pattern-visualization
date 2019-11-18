#!/usr/bin/env python3


import subprocess
## NOTE: Library for heat map generation
import plotly.graph_objects as go
import sys, os, argparse

sys.path.append(os.pardir)
sys.path.append(".")

from utils.constants import *

def get_available_options() -> argparse.Namespace:
    parser_instance = argparse.ArgumentParser(description="Vizualising IO pattern using data gathered via BCC tools.")
    parser_instance.add_argument('-f',  '--filepath', action='store_true', help="Path to file that contains logs gathered via '$ ./iosnoop -s' execution.")
    parser_instance.add_argument('-e', '--execute', action="store", metavar=('PATH', 'AMOUNT'), nargs=2,
                                 help="vizualise certain amount of iosnoop's output logs.")
    general_group = parser_instance.add_argument_group()

    return parser_instance.parse_args()

def visualize_io_pattern(source_file_name):

    # NOTE: Heatmap's data
    heatmap_time_values = []
    heatmap_latency_values = []
    heatmap_bytes_values = []
    heatmap_pid_values = []

    minimal_required_amount_of_data = 7

    IOSNOOP_LOG_FILE_NAME_MOCK = source_file_name
    iosnoop_logs_file = open(IOSNOOP_LOG_FILE_NAME_MOCK)
    lines = []
    current_line = iosnoop_logs_file.readline()

    while (current_line):
        polling_data_values = current_line.split()

        if (len(polling_data_values) < minimal_required_amount_of_data):
            # NOTE: Preventing parsing a single PID (sometimes, the polling ...
            # ... captures this kind of output.
            current_line = iosnoop_logs_file.readline()
            continue
        # TODO: Replace hard-coded index with string pattern (?)
        if (polling_data_values[0] == "STARTs"):
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
    # TODO: Parse bytes values into the buckets
    heatmap_z_values = heatmap_bytes_values
    heatmap_z_labels = [heatmap_bytes_values]

    hovertext = list()
    for yi, yy in enumerate(heatmap_y_values):
        hovertext.append(list())
        # NOTE: Getting the process name by its ID
        print(f"heatmap_pid_values[yi]: {heatmap_pid_values[yi]}")

        cpu = "unknown"
        virtualMemorySize = "unknown"
        ps_cmd_raw_result = []
        target_process_name = "unknown"

        for xi, xx in enumerate(heatmap_x_values):
            hovertext[-1].append(
                'Process name: {} <br />Time: {}<br />Latency: {}<br />Bytes: {} <br /> PID: {}, CPU: {} <br /> Virtual Memory Size: {} <br /> Resident Set Size: {}'.format(
                    target_process_name, xx, yy, heatmap_z_labels[0][yi], heatmap_pid_values[yi], "unknown",
                    "unknown", "unknown"))

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


def main(argv):
    source_file_name = argv[1]
    visualize_io_pattern(source_file_name)

if __name__ == '__main__':

    available_options = get_available_options()
    try:
        if available_options.filepath:
            logs_file_path = available_options.filepath[0]
            visualize_io_pattern(logs_file_path)
        elif available_options.execute:
            iosnoop_script_path = available_options.execute[0]
            required_amount_of_logs_to_capture = available_options.execute[1]
            visualize_io_pattern_with_captured_values(iosnoop_script_path, required_amount_of_logs_to_capture)
            ## TODO: Call the capturing here.
    except Exception as error:
        print(f"Unable to parse given arguments. Details: {error}")
        sys.exit(-1)
    finally:
        sys.exit()
    main(sys.argv)