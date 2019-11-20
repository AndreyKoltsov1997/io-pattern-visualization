
#!/usr/bin/env python3
import sys, os
import re

sys.path.append(os.pardir)
sys.path.append(".")

def is_numberic_value(string_value) -> bool:
    is_floating_point = (re.match(r'^-?\d+(?:\.\d+)?$', string_value) is not None)
    is_integer = string_value.isdigit()
    return (is_floating_point or is_integer)
