from os import mkdir, chdir, listdir

import webbrowser
from time import sleep
import threading
import json
import pkgutil

from minescript import execute, job_info, EventQueue

MSP = False
try:
    from minescript_plus import Util
    MSP = True
except:
    pass

def compute_modules():
    global installed_modules, minescript_scripts
    installed_modules = [module.name for module in pkgutil.iter_modules()]
    minescript_scripts = []

    for module in pkgutil.iter_modules():
        if "minescript" in str(module.module_finder):
            minescript_scripts.append(module.name)

compute_modules()

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


# Get modules for reference


def get_scripts():


    global scripts, categories

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
                dependencies = []

                for line in lines:
                    line = line.strip()
                    if line.startswith("@Name:"):
                        name = line.removeprefix("@Name: ")
                        if name == "@Name:":
                            name = file
                        



                    if line.startswith("@Author:"):
                        author = line.removeprefix("@Author: ")
                        if author == "@Author:":
                            author = ""

                    if line.startswith("@MC:"):
                        mc_details = line.removeprefix("@MC:")



                    if line == "<":
                        transcribe = False

                    if transcribe:
                        description = description +"\n"+ line + "\n"

                    if line == ">":
                        transcribe = True


                    if line.startswith("@Category:"):
                        category = line.removeprefix("@Category: ")
                        if category == "":
                            category = "Uncategorized"

                    if line.startswith("@Version:"):
                        version = line.removeprefix("@Version: ")
                        if line == "@Version:":
                            version = ""

                    if line.startswith("@Link:"):
                        link = line.removeprefix("@Link: ")
                        if line == "@Link:":
                            link = ""
                    if line.startswith("@Required:"):
                        to_cut = line.replace("https://","")
                        segments = to_cut.rpartition(":")
                        modname = segments[0].removeprefix("@Required: ")

                        if len(segments) < 3:
                            dependencies.append(["Unspecified",modname])
                        if segments[2] == "pip":
                            dependencies.append(["pip",modname])

                        if "github" in segments[2]:
                            dependencies.append([segments[2],modname])



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
                        "Link":link,
                        "Dependencies":dependencies
                    }
                #print(dependencies)

                if category not in categories:
                    categories.append(category)
                scripts.append(data)
        categories.append(categories.pop(0))

get_scripts()   

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

def open_github(sender, app_data, user_data):
    webbrowser.open("https:"+user_data)

def open_pip(sender, app_data, user_data):
    if MSP:
        Util.set_clipboard("pip install "+user_data)
        print("Copied!")
    else:
        print("Install Minescript Plus to copy a pip link!")

def edit_menu(sender, app_data, user_data):
    script_name = user_data["Name"]
    
    def close_it():
        dpg.delete_item(script_name+"_window")

    def overwrite_script():
        with open(user_data["Dir"]+".py", "r") as file:
            lines = file.readlines()
            line = 0
            #lines.insert(0,"#Test\n")

            new_data = {
                "Name":dpg.get_value(script_name+"_name"),
                "Author":dpg.get_value(script_name+"_author"),
                "MC":str(dpg.get_value(script_name+"_mc")),
                "Version":dpg.get_value(script_name+"_version"),
                "Category":dpg.get_value(script_name+"_category"),
                "Link":dpg.get_value(script_name+"_link"),
                "Description":dpg.get_value(script_name+"_description")
            }

            last_line = 0
            DESCRIPTION = False
            last_description = 0
            while line < len(lines):

                if "@Name:" in lines[line]:
                    lines.pop(line)
                    lines.insert(line,"@Name: "+new_data["Name"]+"\n")
                    new_data.pop("Name")
                    last_line = line
                if "@Author:" in lines[line]:
                    lines.pop(line)
                    lines.insert(line,"@Author: "+new_data["Author"]+"\n")
                    new_data.pop("Author")
                    last_line = line
                if "@MC:" in lines[line]:
                    lines.pop(line)
                    lines.insert(line,"@MC: "+new_data["MC"]+"\n")
                    new_data.pop("MC")
                    last_line = line
                if "@Version:" in lines[line]:
                    lines.pop(line)
                    lines.insert(line,"@Version: "+new_data["Version"]+"\n")
                    new_data.pop("Version")
                    last_line = line
                if "@Category:" in lines[line]:
                    lines.pop(line)
                    lines.insert(line,"@Category: "+new_data["Category"]+"\n")
                    new_data.pop("Category")
                    last_line = line
                if "@Link:" in lines[line]:
                    lines.pop(line)
                    lines.insert(line,"@Link: "+new_data["Link"]+"\n")
                    new_data.pop("Link")
                    last_line = line
                
                if ">" in lines[line]:
                    DESCRIPTION = True
                    
                
                if "<" in lines[line]:
                    DESCRIPTION = False
                elif DESCRIPTION and not ">" in lines[line]:
                    lines.pop(line)
                    line -= 1
                    


                line += 1
            NEW = False
            if last_line == 0:
                NEW = True
                lines.insert(0,'"""\n')

            keys = new_data.keys()
            for key in keys:
                if key != "Description":
                    lines.insert(last_line,"@"+key+": "+new_data[key]+"\n")
                    
                else:
                    if ">\n" in lines:

                        lines.insert(lines.index(">\n")+1,new_data["Description"]+"\n")
                    else:
                        line = last_line
                        while "@" not in lines[line]:
                            line += 1
                        lines.insert(line+1,">\n"+new_data["Description"]+"\n"+"<\n")
            if NEW:
                lines.insert(0,'"""\n')
        with open(user_data["Dir"]+".py", "w") as file:
            for line in lines:
                file.write(line)
        dpg.delete_item("Viewer Window",children_only=True)
        get_scripts()
        generate_scripts()

    script = user_data
    if script["Name"] == "Unspecified":
        script["Name"] = ""
    if script["Description"] == "No Description.":
        script["Description"] = ""
    if script["Author"] == "Author not found.":
        script["Author"] = ""
    with dpg.window(label="Editor",pos=(50,150),height=400,width=400,tag=script_name+"_window",on_close=close_it):
        dpg.add_text(f"Editing: {script["Name"]}")
        dpg.add_input_text(default_value=script["Name"],label="Script Name",tag=script_name+"_name")
        dpg.add_spacer()
        dpg.add_input_text(default_value=script["MC"].lstrip(" "),label="MC Info",tag=script_name+"_mc")
        dpg.add_spacer()
        dpg.add_input_text(default_value=script["Version"],label="Version Info",tag=script_name+"_version")
        dpg.add_spacer()
        dpg.add_input_text(default_value=script["Author"],label="Author(s)",tag=script_name+"_author")
        dpg.add_spacer()
        dpg.add_input_text(default_value=script["Link"],label="Link",tag=script_name+"_link")
        dpg.add_spacer()
        dpg.add_input_text(default_value=script["Category"],label="Category",tag=script_name+"_category")
        dpg.add_spacer()
        dpg.add_input_text(default_value=script["Description"].lstrip("\n").rstrip("\n"),label="Description \n(CTRL + Enter \nfor new line)",ctrl_enter_for_new_line=True,multiline=True,tag=script_name+"_description")
        dpg.add_button(label="Save",callback=overwrite_script)

def generate_scripts():
    for category in categories:
            category_length = 0
            for script in scripts:
                if script["Category"] == category:
                    category_length += 1
            with dpg.collapsing_header(label=category +f" ({category_length})",parent="Viewer Window"):
                with dpg.child_window(height=500):
                                for script in scripts:
                                    if script["Category"] == category:
                                        with dpg.collapsing_header(label=script["Name"]):
                                            with dpg.child_window(height=300):

                                                with dpg.tree_node(label="Info",default_open=True):
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
                                                    dpg.add_button(label="Edit",callback=edit_menu,user_data=script)

                                                if script["Dependencies"] != []:
                                                    with dpg.tree_node(label="Dependencies"):
                                                        dependencies = script["Dependencies"]
                                                        #print(dependencies)
                                                        for dependency in dependencies:
                                                            name = dependency[1]
                                                            if name in installed_modules:
                                                                indicator = "[X]"
                                                            else:
                                                                indicator = "[ ]"
                                                            if dependency[0] == "pip":
                                                                dpg.add_button(label=f"{indicator} {dependency[1]} via pip",callback=open_pip,user_data=dependency[1])

                                                            elif "github" in dependency[0]:
                                                                dpg.add_button(label=f"{indicator} {dependency[1]} via Github",callback=open_github,user_data=dependency[0])

                                                dpg.add_text(label="")
                                                dpg.add_checkbox(label="Run", callback=executor,user_data=script["Dir"])

with dpg.window(label="Launcher", width=600,height=300, tag="Main"):
    

    with dpg.child_window(label="Viewer",tag="Viewer Window"):
        generate_scripts()
                
                                    



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

