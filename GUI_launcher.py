from os import mkdir, chdir, listdir

import webbrowser
from time import sleep
import threading

from minescript import execute, job_info, EventQueue


NAME = "launcher"

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

try:
    chdir(NAME)
except:
    mkdir(NAME)
    print(f"This script has created a folder in your minescript folder named '{NAME}'. Place your scripts into that folder in order to have this script recognize them.")
    exit()

try:
    import dearpygui.dearpygui as dpg
except:
    print(f"This script requires the dearpygui module to operate. Install it in your python instance using 'py -m pip install dearpygui' and the re-run this script. You're almost there ;)")
    exit()

# Initialize
scripts = []
categories = []


for file in listdir():
    if file.endswith(".py"):
        with open(file, 'r') as script:


            transcribe = False
            description = ""
            name = ""
            author = ""
            category = "Uncategorized"
            version = ""
            link = ""


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
                
            data = {
                    "Name":name,
                    "Description":description,
                    "Author":author,
                    "Category":category,
                    "MC":mc_details,
                    "Version":version,
                    "Dir":NAME+"/"+file.removesuffix(".py"),
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

    
    


with dpg.window(label="Launcher", width=600,height=300, tag="Main"):
    

    with dpg.child_window(label="Viewer"):

        for category in categories:
            with dpg.collapsing_header(label=category):
                
                with dpg.child_window():
                    for script in scripts:
                        if script["Category"] == category:
                            with dpg.collapsing_header(label=script["Name"]):
                                
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
threading.Thread(target=keep_awake).start()


dpg.start_dearpygui()
dpg.destroy_context()

