#!/usr/bin/env python3

import sys, os, argparse

sys.path.append(os.pardir)
sys.path.append(".")

from visualization.heatmap_utils import *

def get_available_options() -> argparse.Namespace:
    parser_instance = argparse.ArgumentParser(description="Vizualising IO pattern using data gathered via BCC tools.")
    parser_instance.add_argument('-f',  '--filepath', action='store', metavar=('FILEPATH'), nargs=1,
                                 help="Path to file that contains logs gathered via '$ ./iosnoop -s' execution.")
    parser_instance.add_argument('-e', '--execute', action="store", metavar=('PATH', 'AMOUNT'), nargs=2,
                                 help="vizualize certain amount of iosnoop's output logs.")
    general_group = parser_instance.add_argument_group()
    return parser_instance.parse_args()

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
        sys.exit(0)
    except Exception as error:
        print(f"Unable to parse given arguments. Details: {error}")
        sys.exit(-1)
    finally:
        sys.exit()
