#!/usr/bin/env python3

import sys, os, argparse

sys.path.append(os.pardir)
sys.path.append(".")

from visualization.heatmap_utils import *

def get_available_options() -> argparse.Namespace:
    parser_instance = argparse.ArgumentParser(description="Vizualising IO pattern using data gathered via BCC tools.")
    parser_instance.add_argument('-f',  '--filepath', action='store', metavar=('FILEPATH', 'KIND'), nargs=2,
                                 help="Path to file that contains logs gathered via '$ ./iosnoop -s' execution.")
    parser_instance.add_argument('-e', '--execute', action='store', metavar=('PATH', 'AMOUNT', 'KIND'), nargs=3,
                                 help="Visualize certain amount of iosnoop's output logs.")
    parser_instance.add_argument('-l', '--load', action='store', metavar='FOLDERPATH', nargs=1,
                                 help="Path to folder with .dat files for visualization.")
    general_group = parser_instance.add_argument_group()
    return parser_instance.parse_args()

if __name__ == '__main__':
    available_options = get_available_options()
    try:
        if available_options.filepath:
            logs_file_path = available_options.filepath[0]
            logs_kind = available_options.filepath[1]
            visualize_io_pattern(logs_file_path, logs_kind)
        elif available_options.execute:
            iosnoop_script_path = available_options.execute[0]
            required_amount_of_logs_to_capture = available_options.execute[1]
            visualize_io_pattern_with_captured_values(iosnoop_script_path, required_amount_of_logs_to_capture)
        elif available_options.load:
            directory_with_sources_path = available_options.load[0]
            figures_html_files = []
            for source_log_file in os.listdir(directory_with_sources_path):
                # NOTE: Generating core figures for every log file found.
                log_file_relative_path = f"{directory_with_sources_path}/{source_log_file}"
                figures_generated_from_log_file = get_core_charts_from_file(log_file_relative_path, source_log_file)
                for figure_index, figure in enumerate(figures_generated_from_log_file):
                    # NOTE: Generating HTML file for every core figure. It's done in order ..
                    # ... to reduce data stored within RAM.
                    tmp_html_file_name = f"{figure_index}-{source_log_file}.html"
                    generete_html_for_figure(figure, tmp_html_file_name)
                    figures_html_files.append(tmp_html_file_name)
            merge_html_files(figures_html_files, "result_all")
        sys.exit(0)
    except Exception as error:
        print(f"Unable to parse given arguments. Details: {error}")
        sys.exit(-1)
    finally:
        sys.exit()
