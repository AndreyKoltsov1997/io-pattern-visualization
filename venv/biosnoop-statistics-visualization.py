import time
import subprocess

BIOSNOOP_MOCK_SCRIPT_NAME = "biosnoop-output-mock.sh"

biosnoop_process = subprocess.Popen(['./{biosnoop_mock}'.format(biosnoop_mock=BIOSNOOP_MOCK_SCRIPT_NAME)], shell=True, stdout=subprocess.PIPE)
while biosnoop_process.poll() is None:
    pollingResult = biosnoop_process.stdout
    line = pollingResult.readline().decode("utf-8")
    print(line)
    time.sleep(0.5)

