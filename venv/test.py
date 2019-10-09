# import subprocess
# subprocess.call(['chmod', '+x', 'test-forever-output.sh'])
#
# subprocess.call(['./test-forever-output.sh'], shell=True, stdout=subprocess.PIPE)

import io
import time
import subprocess
import sys

process = subprocess.Popen(['./test-forever-output.sh'], shell=True, stdout=subprocess.PIPE)
while process.poll() is None:
    pollingResult = process.stdout
    print(pollingResult)
    time.sleep(0.5)
