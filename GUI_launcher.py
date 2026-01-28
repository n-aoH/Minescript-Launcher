from os import mkdir, chdir, listdir

import webbrowser
from time import sleep
import threading
import json


from minescript import execute, job_info, EventQueue





"""
@Name: GUI Launcher
@Author: @No
@MC: Tested on 1.21.10. Works on all versions.
@Version: 1
@Category: INFO
@Link: https://github.com/n-aoH/Minescript-Launcher/tree/main


>
A script made to collect and organize your own scripts.
Launches scripts with an API to communicate to it.
<

"""


try:
    chdir("minescript") #future proofing
except:
    pass

default_config = {
    "Path":"launcher",
    "Data Path Name":"launcher data",
    "Confined":False
}

first_time = True
def readcfg():
    global config, first_time
    try:

        with open("launcher_config.json", "x") as file:
            json.dump(default_config,file)
        config = default_config
    except FileExistsError:

        with open("launcher_config.json", "r") as file:
            config = json.load(file)
        first_time = False
        
readcfg()    








try:
    import dearpygui.dearpygui as dpg
except:
    print(f"This script requires the dearpygui module to operate. Install it in your python instance using 'py -m pip install dearpygui' and the re-run this script. You're almost there ;)")
    exit()

def confied_dropdown(sender, data):
    global default_config
    default_config["Confined"]= not "Use" in data

def path_dropdown(sender, data):
    global default_config
    default_config["Path"]= data

def path_data(sender, data):
    global default_config
    default_config["Data Path Name"] = data
if first_time:
    dpg.create_context()
    dpg.create_viewport(title='Minescript GUI Launcher', width=650, height=300)
    with dpg.window(label="Launcher", width=750,height=300, tag="Main"):

        dpg.add_text("Welcome! You are seeing this pop-up because it is your first time using this script.")
        
        with dpg.child_window():
            dpg.add_text("Would  You like for this script to use the '/minescript' directory or its own?")
            dpg.add_combo(items=["Use '/minescript' (fastest onboarding)", "Create a new directory (Drop scripts into there for this script to recognize them)"],
                          callback=confied_dropdown,default_value="Use '/minescript' (fastest onboarding)")

            dpg.add_spacer()

            dpg.add_text("Isolated Script path: ")
            dpg.add_input_text(default_value=default_config["Path"],callback=path_dropdown)

            dpg.add_spacer()

            dpg.add_text("Data folder name:")
            dpg.add_input_text(default_value=default_config["Data Path Name"],callback=path_data)

            dpg.add_spacer()

            dpg.add_button(label="Done!",callback=dpg.stop_dearpygui, width=100, height= 20)
    dpg.set_primary_window("Main",True)

    


    dpg.setup_dearpygui()

    
    dpg.show_viewport()


    dpg.start_dearpygui()

    with open("launcher_config.json", "w") as file:
        json.dump(default_config,file)
    config = default_config

    
    dpg.destroy_context()

CONFINED = config["Confined"]

NAME = config["Path"]

if CONFINED:
    try:
        chdir(NAME)
    except:
        mkdir(NAME)
        print(f"This script has created a folder in your minescript folder named '{NAME}'. Place your scripts into that folder in order to have this script recognize them.")
        exit()
# Initialize
scripts = []
categories = ["Uncategorized"]


for file in listdir():
    if file.endswith(".py"):
        with open(file, 'r') as script:


            transcribe = False
            description = ""
            name = file.removesuffix(".py")
            author = ""
            category = "Uncategorized"
            version = ""
            link = ""
            mc_details = "Unspecified."


            lines = script.readlines()


            for line in lines:
                line = line.strip()
                if line.startswith("@Name:"):
                    name = line.removeprefix("@Name: ")
                    


                if line.startswith("@Author:"):
                    author = line.removeprefix("@Author: ")
                    

                if line.startswith("@MC:"):
                    mc_details = line.removeprefix("@MC:")
                    


                if line == "<":
                    transcribe = False

                if transcribe:
                    description = description +"\n"+ line + "\n"

                if line == ">":
                    transcribe = True

                if line.startswith("@Category:"):
                    category = line.lstrip("@Category: ")

                if line.startswith("@Version:"):
                    version = line.lstrip("@Version: ")

                if line.startswith("@Link:"):
                    link = line.lstrip("@Link: ")
            if CONFINED:
                directory = NAME+"/"+file.removesuffix(".py")
            else:
                directory = file.removesuffix(".py")
            data = {
                    "Name":name,
                    "Description":description,
                    "Author":author,
                    "Category":category,
                    "MC":mc_details,
                    "Version":version,
                    
                    "Dir":directory,
                    "Link":link
                }
            

            if category not in categories:
                categories.append(category)
            scripts.append(data)

            

dpg.create_context()
dpg.create_viewport(title='Minescript GUI Launcher', width=600, height=1000)


def executor(sender, data, user_data):
    for job in job_info():
        
        
        cmd = job.command[0].replace("\\","/")

        if not data:
            if user_data in cmd: #Already Exists

                if job.self != True:
                    execute(f"\\killjob {job.job_id}")
                    return
        else:
            #Doesn't exist
            execute(f"\\{user_data}")
            return

    
    
categories.append(categories.pop(0))

with dpg.window(label="Launcher", width=600,height=300, tag="Main"):
    

    with dpg.child_window(label="Viewer"):

        for category in categories:
            with dpg.collapsing_header(label=category):
                
                with dpg.child_window(height=500):
                    for script in scripts:
                        if script["Category"] == category:
                            with dpg.collapsing_header(label=script["Name"]):
                                with dpg.child_window(height=300):
                                
                                    if script["MC"] != "":
                                        dpg.add_text("MC Info: "+script["MC"])


                                    if script["Version"] != "":
                                        dpg.add_text("Version: "+script["Version"])

                                    if script["Description"] != "":
                                        dpg.add_text(script["Description"])
                                    else:
                                        dpg.add_text("No Description.")

                                    if script["Author"] != "":
                                        dpg.add_text("Made by: "+script["Author"])
                                    else:
                                        dpg.add_text("Author not found.")

                                    if script["Link"] != "":
                                        dpg.add_button(label="Repo Link",callback= lambda: webbrowser.open(script["Link"]))

                                    dpg.add_text(label="")
                                    dpg.add_checkbox(label="Run", callback=executor,user_data=script["Dir"])



dpg.set_primary_window("Main",True)
dpg.setup_dearpygui()
dpg.show_viewport()

def keep_awake():
    with EventQueue() as event_queue:
        event_queue.register_world_listener()
        while True:
            sleep(500)
threading.Thread(target=keep_awake, daemon=True).start()


dpg.start_dearpygui()
dpg.destroy_context()

