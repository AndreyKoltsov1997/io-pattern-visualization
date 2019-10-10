import time
import subprocess
import plotly.graph_objects as go ## Library for heat map
import random

# NOTE: Retrieving the info about the process
PROCESS_NAME_MOCK = "postgres"
ps_cmd_result = subprocess.run(['ps aux | grep {process_name}'.format(process_name=PROCESS_NAME_MOCK)], shell=True, stdout=subprocess.PIPE)
ps_cmd_raw_result = ps_cmd_result.stdout.decode("utf-8").split()
print("ps_cmd_values", ps_cmd_raw_result)

exit(1) # TODO: Delete debug exit

BIOSNOOP_MOCK_SCRIPT_NAME = "biosnoop-output-mock.sh"

biosnoop_process = subprocess.Popen(['./{biosnoop_mock}'.format(biosnoop_mock=BIOSNOOP_MOCK_SCRIPT_NAME)], shell=True, stdout=subprocess.PIPE)
# NOTE: Heatmap's data
heatmap_time_values = []
heatmap_latency_values = []
heatmap_bytes_values = []
heatmap_pid_values = []

minimal_required_amount_of_data = 5
# while biosnoop_process.poll() is None:
while (len(heatmap_time_values) < 100):
    polling_result = biosnoop_process.stdout
    polling_data_values = polling_result.readline().decode("utf-8").split()
    if (len(polling_data_values) < minimal_required_amount_of_data):
        # NOTE: Preventing parsing a single PID (sometimes, the polling ...
        # ... captures this kind of output.
        continue
    # TODO: Replace hard-coded index with string pattern (?)
    heatmap_time_values.append(polling_data_values[0])
    # print(polling_data_values)
    heatmap_pid_values.append(polling_data_values[2])
    heatmap_bytes_values.append(polling_data_values[6])
    heatmap_latency_values.append(polling_data_values[7])
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
    for xi, xx in enumerate(heatmap_x_values):
        hovertext[-1].append('Time: {}<br />Latency: {}<br />Bytes: {} <br /> PID: {}'.format(xx, yy, heatmap_z_labels[0][yi], heatmap_pid_values[yi]))

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