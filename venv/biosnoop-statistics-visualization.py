import time
import subprocess
import plotly.graph_objects as go ## Library for heat map
import random

BIOSNOOP_MOCK_SCRIPT_NAME = "biosnoop-output-mock.sh"

biosnoop_process = subprocess.Popen(['./{biosnoop_mock}'.format(biosnoop_mock=BIOSNOOP_MOCK_SCRIPT_NAME)], shell=True, stdout=subprocess.PIPE)
# NOTE: Heatmap's data
heatmap_time_values = []
heatmap_latency_values = []
heatmap_bytes_values = []
heatmap_pid_values = []

minimal_required_amount_of_data = 5
# while biosnoop_process.poll() is None:
while (len(heatmap_pid_values) < 100):
    polling_result = biosnoop_process.stdout
    polling_data_values = polling_result.readline().decode("utf-8").split()
    if (len(polling_data_values) < minimal_required_amount_of_data):
        # NOTE: Preventing parsing a single PID (sometimes, the polling ...
        # ... captures this kind of output.
        continue
    # TODO: Replace hard-coded index with string pattern (?)
    heatmap_time_values.append(polling_data_values[0])
    heatmap_pid_values.append(polling_data_values[2])
    heatmap_bytes_values.append(polling_data_values[5])
    heatmap_latency_values.append(polling_data_values[6])

    # time.sleep(0.2)

# heatmap_x_values = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
# heatmap_y_values = ['Morning', 'Afternoon', 'Evening']
# heatmap_z_values = [[1, 20, 30, 50, 1], [20, 1, 60, 80, 30], [300, 60, 1, -10, 20]]

heatmap_z_values = [[i + random.random() for i in range(len(heatmap_time_values))] for ii in range(len(heatmap_pid_values))]


hovertext = list()
for yi, yy in enumerate(heatmap_pid_values):
    hovertext.append(list())
    for xi, xx in enumerate(heatmap_time_values):
        hovertext[-1].append('Disk: {}<br />Time: {}<br />Latency: {}'.format(xx, yy, heatmap_z_values[yi][xi]))


disk_number_mock = 1
io_pattern_heat_map = go.Figure(data=go.Heatmap(
                   z=heatmap_z_values,
                   x=heatmap_time_values,
                   y=heatmap_pid_values,
                   hoverinfo='text',
                   text=hovertext))

io_pattern_heat_map.update_layout(
    title='BIOSNOOP statistics',
    xaxis_nticks=36)

io_pattern_heat_map.show()