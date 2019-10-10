import time
import subprocess

BIOSNOOP_MOCK_SCRIPT_NAME = "biosnoop-output-mock.sh"

test_forever_output = subprocess.Popen(['./{biosnoop_mock}'.format(biosnoop_mock=BIOSNOOP_MOCK_SCRIPT_NAME)], shell=True, stdout=subprocess.PIPE)
while test_forever_output.poll() is None:
    pollingResult = test_forever_output.stdout
    line = pollingResult.readline().decode("utf-8")
    print(line)
    time.sleep(0.5)

