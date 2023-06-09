
import ctypes
import psutil
import yaml
from pythonosc import udp_client
import time

# Loads config file
config_file = "VRCatchApp/config.yaml"
blocked_processes = []

with open(config_file, "r") as f:
    config = yaml.safe_load(f)
    blocked_processes = config.get("blocked_processes", [])
    In_app = config.get("info_text", [])

client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

user32 = ctypes.windll.user32
GetForegroundWindow = user32.GetForegroundWindow
GetWindowThreadProcessId = user32.GetWindowThreadProcessId

def get_application_name(pid):

    try:
        process = psutil.Process(pid)
        return process.name().split(".exe")[0]
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""

previous_application_name = ""
cooldown_start_time = 0
cooldown_duration = 4  # cooldown to prevent spam on VRChat when changing apps too fast 

# Checking if application is focused
while True:
    hwnd = GetForegroundWindow()
    pid = ctypes.c_ulong()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process_id = pid.value
    current_time = time.time()

    if process_id > 0:
        application_name = get_application_name(process_id)
        if (
            application_name
            and application_name != previous_application_name
            and (current_time - cooldown_start_time) >= cooldown_duration
        ):
            print("Catched app:", application_name)
            for blocked_process in blocked_processes:
                if application_name == blocked_process["process"]:
                    message = blocked_process["message"]
                    print(message)
                    client.send_message("/chatbox/input", message)
                    break
                else: 
                    client.send_message("/chatbox/input", "➡️ In app: " + application_name) #You can change message here
                    previous_application_name = application_name
                    cooldown_start_time = current_time

"""
VRCatchApp © 2023 DeJzer
"""