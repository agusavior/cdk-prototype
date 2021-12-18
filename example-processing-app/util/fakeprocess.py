from time import time

# Simulate a CPU bound process for `seconds` seconds
def fake_process(seconds: int):
    start_time = time()
    a = 0
    while time() - start_time < seconds:
        a += 1
        a -= 1
