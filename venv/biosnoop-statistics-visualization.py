import subprocess
## NOTE: Library for heat map generation
import plotly.graph_objects as go
import sys

def visualize_io_pattern(amount_of_logs_to_collect, source_file_name):

    # NOTE: Heatmap's data
    heatmap_time_values = []
    heatmap_latency_values = []
    heatmap_bytes_values = []
    heatmap_pid_values = []

    minimal_required_amount_of_data = 7
    # while biosnoop_process.poll() is None:
    TIME_VALUE_INDEX = 0
    PID_VALUE_INDEX = 2
    BYTES_VALUE_INDEX = 6
    LATENCY_VAUE_INDEX = 7

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

        heatmap_time_values.append(polling_data_values[TIME_VALUE_INDEX])
        heatmap_pid_values.append(polling_data_values[PID_VALUE_INDEX])
        heatmap_bytes_values.append(polling_data_values[BYTES_VALUE_INDEX])
        heatmap_latency_values.append(polling_data_values[LATENCY_VAUE_INDEX])
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


def main(argv):
    amount_of_logs_to_analyze = int(argv[1])
    source_file_name = argv[2]
    visualize_io_pattern(amount_of_logs_to_analyze, source_file_name)

if __name__ == '__main__':
    main(sys.argv)