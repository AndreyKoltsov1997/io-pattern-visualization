import time
import subprocess
import plotly.graph_objects as go ## Library for heat map

BIOSNOOP_MOCK_SCRIPT_NAME = "biosnoop-output-mock.sh"

biosnoop_process = subprocess.Popen(['./{biosnoop_mock}'.format(biosnoop_mock=BIOSNOOP_MOCK_SCRIPT_NAME)], shell=True, stdout=subprocess.PIPE)
minimal_required_amount_of_data = 5
while biosnoop_process.poll() is None:
    polling_result = biosnoop_process.stdout
    polling_data_values = polling_result.readline().decode("utf-8").split()
    if (len(polling_data_values) < minimal_required_amount_of_data):
        continue
    print(polling_data_values)
    time.sleep(0.5)

heatmap_x_values = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
heatmap_y_values = ['Morning', 'Afternoon', 'Evening']
heatmap_z_values = [[1, 20, 30, 50, 1], [20, 1, 60, 80, 30], [300, 60, 1, -10, 20]]

hovertext = list()
for yi, yy in enumerate(heatmap_y_values):
    hovertext.append(list())
    for xi, xx in enumerate(heatmap_x_values):
        hovertext[-1].append('Disk: {}<br />Time: {}<br />Latency: {}'.format(xx, yy, heatmap_z_values[yi][xi]))


disk_number_mock = 1
io_pattern_heat_map = go.Figure(data=go.Heatmap(
                   z=heatmap_z_values,
                   x=heatmap_x_values,
                   y=heatmap_y_values,
                   hoverinfo='text',
                   text=hovertext))

io_pattern_heat_map.update_layout(
    title='BIOSNOOP statistics',
    xaxis_nticks=36)

io_pattern_heat_map.show()