import subprocess
## NOTE: Library for heat map generation
import plotly.graph_objects as go
import sys

def visualize_io_pattern(bcc_tools_location, amount_of_logs_to_collect):

    biosnoop_process = subprocess.Popen(['python {biosnoop_script_location}'.format(biosnoop_script_location=bcc_tools_location)],
                                        shell=True, stdout=subprocess.PIPE)
    # NOTE: Heatmap's data
    heatmap_time_values = []
    heatmap_latency_values = []
    heatmap_bytes_values = []
    heatmap_pid_values = []

    minimal_required_amount_of_data = 5
    # while biosnoop_process.poll() is None:
    TIME_VALUE_INDEX = 0
    PID_VALUE_INDEX = 2
    BYTES_VALUE_INDEX = 6
    LATENCY_VAUE_INDEX = 7

    while (len(heatmap_time_values) < amount_of_logs_to_collect):
        polling_result = biosnoop_process.stdout

        polling_data_values = polling_result.readline().decode("utf-8").split()

        if (len(polling_data_values) < minimal_required_amount_of_data):
            # NOTE: Preventing parsing a single PID (sometimes, the polling ...
            # ... captures this kind of output.
            continue
        # TODO: Replace hard-coded index with string pattern (?)

        heatmap_time_values.append(polling_data_values[TIME_VALUE_INDEX])
        heatmap_pid_values.append(polling_data_values[PID_VALUE_INDEX])
        heatmap_bytes_values.append(polling_data_values[BYTES_VALUE_INDEX])
        heatmap_latency_values.append(polling_data_values[LATENCY_VAUE_INDEX])
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
    try:
        LOGS_FILE_SOURCE_FILE_MOCK = "iosnoop_logs.dat"
        iosnoop_logs_file = open(LOGS_FILE_SOURCE_FILE_MOCK, "r")
        should_continue_reading_file = True
        while (True):
            current_line = iosnoop_logs_file.readline()
            should_continue_reading_file = (current_line)
            print(f'current_line: {current_line}')
        # bcc_tools_script_location = argv[1]
        # amount_of_logs_to_collect = int(argv[2])
        # visualize_io_pattern(bcc_tools_script_location, amount_of_logs_to_collect)
    except Exception as error:
        print("Path to BCC tools hasn't been specified.")
        print("USE: $ python3 biosnoop-statistics-visualization.py <path_to_bcc_tools> <amount_of_metrics_to_collect>")
        sys.exit(-1)


if __name__ == '__main__':
    main(sys.argv)