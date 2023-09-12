from simulation.unity_simulator.comm_unity import UnityCommunication
import subprocess
import time
UTILITY_SIM_PATH = "/home/liam/installs/virtual_home_exe/linux_exec.v2.2.4.x86_64"

def start_sim():
    subp = subprocess.Popen([f"{UTILITY_SIM_PATH}"])
    time.sleep(5)
    return subp
def stop_sim(sim):
    try:
        sim.kill()
    except Exception as e:
        print(f"Failed to end simulation: {e}")
