from minescript import *
import lib_launcher as launcher
from random import uniform
from time import sleep
import threading

"""
@Name: Auto Reply
@Author: @No
@MC: Works on all versions.
@Version: 1.0
@Link: https://github.com/n-aoH/Minescript-Launcher/blob/main/examples/auto_reply.py
@Category: Macros
@Required: lib_launcher

>
A very primitive macro that 
responds directly in chat when a 
string is recieved. 
Created to show of lib_launcher's
API.
<
"""

# Define the settings to be used. Adding to these will be updated, but taking away will not. Delete file/overwrite to regen it.
default_settings = {
    "Keyword":"input",
    "Output":"Output",
    "Min":0.3,
    "Max":0.7,
    "Character Delay":0.1
}

# Call this every time it updates
def on_update(data):
    global keyword, min_time, max_time, output, char_delay
    keyword = data["Keyword"]
    min_time = data["Min"]
    max_time = data["Max"]
    output = data["Output"]
    char_delay = data["Character Delay"]
    print("Updated!")

settings = launcher.initialize(default_settings)
on_update(settings)

launcher.monitor(on_update)


def do(cmd):
    if cmd.startswith("/") or cmd.startswith("\\"):
        exec(cmd)
    else:
        chat(cmd)



with EventQueue() as event_queue:
    event_queue.register_chat_listener()
    
    while True:
        event = event_queue.get()
        
        if keyword in event.message.lower():
            sleep(uniform(min_time,max_time) + len(output) * char_delay)
            do(output)

