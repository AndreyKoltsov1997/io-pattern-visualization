import time
import subprocess

test_forever_output = subprocess.Popen(['./biosnoop-output-mock.sh'], shell=True, stdout=subprocess.PIPE)
while test_forever_output.poll() is None:
    pollingResult = test_forever_output.stdout
    line = pollingResult.readline().decode("utf-8")
    print(line)
    time.sleep(0.5)

