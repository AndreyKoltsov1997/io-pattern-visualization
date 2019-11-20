# IO pattern visualization tool.

## Purpose 
Visualizing the IO-related data via the Heat Map. What makes it unique is the additional info about the process that performs the IO operations. 

## Heatmap example 
![](media/heatmap-example.png)<br/>
## Usage

```
$ pip install plotly 
$ python3 ./biosnoop-statistics-visualization.py <path_to_bcc_tools> <amount_of_metrics_to_collect>
```
* *<path_to_bcc_tools>*  - path to the valid BCC tools file. The implementation has been tested using BIOSNOOP;
* *<amount_of_metrics_to_collect>* - amount of metrics to collection from the script launched from <path_to_bcc_tools>;

## 3.2 Available options

To get actual list of all options run: `./utils/pks_manager.py -h`

                                 
| Option | Short flag | Params | Description |
| --- | --- | --- | --- |
| --filepath | -f | [FILEPATH] [KIND] | Visualize data from given file. [FILEPATH] - Path to file, [KIND] - string description of the data.  |
| --execute | -e | [PATH] [AMOUNT] [KIND} | Visualize data based on the captured output of iosnoop. [PATH] - path to IOSNOOP executable, [AMOUNT] - amount of logs to process, [KIND] - string description of the data. |
| --load | -l | [FOLDERPATH] | Visualize data from every file within given folder. [FOLDERPATH] - path to folder that contains files with logs. |
 
 > Note: It is recommended use a test-id for the name of the new cluster, which can be generated with `./test.py -id` command. 
>
After that, the heatmap will be opened within your browser.

