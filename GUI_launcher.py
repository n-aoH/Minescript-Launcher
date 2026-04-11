from os import mkdir, chdir, listdir

import webbrowser
from time import sleep
import threading
import json
import pkgutil
import time
import urllib
import urllib.request
from urllib.parse import urlparse
import datetime

from minescript import *


try:
    from java import JavaClass
except:
    from lib_java import JavaClass

MSP = True
try:
    from minescript_plus import Util
    
except ModuleNotFoundError:
    MSP = False
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

window = False

### EMBEDDED FROM MSP

try:
    Minecraft = JavaClass("net.minecraft.client.Minecraft")
except:
    print("Mappings Required! Run '\\install_mappings' in chat to get them!")
    exit(1)
mc = Minecraft.getInstance()
def get_clipboard() -> str:
    """
    Retrieves the current contents of the system clipboard.
    Returns:
        str: The text currently stored in the clipboard.
    """
    return mc.keyboardHandler.getClipboard() # type: ignore


def set_clipboard(string: str):
    """
    Sets the system clipboard to the specified string.
    Args:
        string (str): The text to be copied to the clipboard.
    """
    mc.keyboardHandler.setClipboard(string)




"""
@Name: GUI Launcher
@Author: @No
@MC: Tested on 1.21.10. Works on all versions.
@Version: 4
@Category: INFO
@Link: https://github.com/n-aoH/Minescript-Launcher/edit/main/GUI_launcher.py
@Required: minescript_plus

>
A script made to collect and organize your own scripts.
Launches scripts with an API to communicate to it.
<
"""


try:
    chdir("minescript") #future proofing
except:
    pass

### MSP Integration: Version

import ast

def get_ver(path: str):
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)

    for node in tree.body:
        # Handles: _ver = "..."
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_ver":
                    return ast.literal_eval(node.value)

        # Handles: _ver: str = "..."
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "_ver":
                return ast.literal_eval(node.value)

    return None

if MSP:
    msp_ver = get_ver("minescript_plus.py")
    




default_config = {
    "Path":"launcher",
    "Data Path Name":"launcher data",
    "Confined":False,
    "Always On Top":False,
    "Hide Except Screens":False,
    "Inventory Screens Only":True,
    "Hotload Delay":0.1,
    "Lib Launcher Min Time":0.1
}

def save_settings():
    with open("launcher_config.json", "w") as file:
        json.dump(config,file)

MONITOR_DELAY = 0.1
first_time = True
def readcfg():
    global config, first_time, MONITOR_DELAY
    try:

        with open("launcher_config.json", "x") as file:
            json.dump(default_config,file)
        config = default_config
    except FileExistsError:

        with open("launcher_config.json", "r") as file:
            config = default_config
            
            cfg = json.load(file)
            for key in cfg:
                config[key] = cfg[key]
        save_settings()
        first_time = False
        MONITOR_DELAY = config["Hotload Delay"]
readcfg()    








try:
    import dearpygui.dearpygui as dpg
except:
    print(f"This script requires the dearpygui module to operate. Install it in your python instance using 'python -m pip install dearpygui' and the re-run this script. You're almost there ;)")
    set_clipboard("python -m pip install dearpygui")
    print("Command coppied to clipboard for convenience.")
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






last_updated_settings = {}
def get_settings_for_script():
    """
    Gets the script settings updates since it was last called.

    dict["path"] = settings (JSON)
    """
    global last_updated_settings
    script_settings = {}
    currenttime = time.time()
    keys = last_updated_settings.keys()
    
    data_dir = config["Data Path Name"]+"/"
    settings_paths = os.listdir("launcher data")
    for path in settings_paths:
        
        if path.endswith(".json"):
            if path in keys: #If it's indexed

                if last_updated_settings[path] != os.path.getmtime(data_dir+path): #If it was updated

                    with open(data_dir+path, "r") as file:
                        script_settings[path] =  json.load(file)
                        last_updated_settings[path] = os.path.getmtime(data_dir+path)

            else:
                last_updated_settings[path] = os.path.getmtime(data_dir+path)

                with open(data_dir+path, "r") as file:
                        script_settings[path] =  json.load(file)
        
        elif path.endswith(".notif"):
            data = {}
            with open(data_dir+path, "r",encoding="utf-8") as file:
                data = json.load(file)
            make_notification(data["Title"],data["Content"],path)
            os.remove(data_dir+path)
    
    return script_settings


    

# Get modules for reference


def get_scripts():


    global scripts, categories

    scripts = []
    categories = ["Uncategorized"]
    for file in listdir():
        if file.endswith(".py") or file.endswith(".pyj"):
            with open(file, 'r') as script:


                transcribe = False
                description = ""
                name = file.removesuffix(".py").removesuffix(".pyj")
                author = ""
                category = "Uncategorized"
                version = ""
                link = ""
                mc_details = "Unspecified."
                pyjinn = file.endswith(".pyj")


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
                    directory = NAME+"/"+file.removesuffix(".py").removesuffix(".pyj")
                else:
                    directory = file.removesuffix(".py").removesuffix(".pyj")
                data = {
                        "Name":name,
                        "Description":description,
                        "Author":author,
                        "Category":category,
                        "MC":mc_details,
                        "Version":version,

                        "Dir":directory,
                        "Link":link,
                        "Dependencies":dependencies,
                        "Pyjinn":pyjinn
                    }
                #print(dependencies)

                if category not in categories:
                    categories.append(category)
                scripts.append(data)
                
        categories.append(categories.pop(0))

get_scripts()   


def import_from_github(sender, app_data, user_data=""): #user_data is additional path stuff
    url = app_data
    raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

    filename = os.path.basename(urlparse(url).path)

    urllib.request.urlretrieve(raw_url, user_data+filename)
    echo("Successfully imported "+filename+" !")
    if window:
        make_notification("Import Successful!",filename)

dpg.create_context()

FIRST_FONT = True
internal_fonts = {
    "Standard":[r"https://github.com/n-aoH/Minescript-Launcher/blob/dev/launcher%20data/Roboto-Regular.ttf","Roboto-Regular.ttf",16],
    "Bold":[r"https://github.com/n-aoH/Minescript-Launcher/blob/dev/launcher%20data/Roboto-Bold.ttf","Roboto-Bold.ttf",20],
    "Notification":[r"https://github.com/n-aoH/Minescript-Launcher/blob/dev/launcher%20data/Roboto-Medium.ttf","Roboto-Medium.ttf",20]
    
    }

os.makedirs(config["Data Path Name"], exist_ok=True)

def getfont(title):
    global FIRST_FONT
    
    name = internal_fonts[title][1]
    path = os.path.join(config["Data Path Name"], name)

    if os.path.exists(path):
        
        font = config["Data Path Name"]+"/"+name
        
    else:
        if FIRST_FONT:
            print("This script requires Additional assets (fonts, images, etc). They will be downloaded from the official github page in 3..")
            sleep(1)
            print("2..")
            sleep(1)
            print("1..")
            sleep(1)
        import_from_github(sender=None,app_data=internal_fonts[title][0],user_data=config["Data Path Name"]+"/")
        sleep(0)
        
        font = config["Data Path Name"]+"/"+name
        
    FIRST_FONT = False
    return font

fonts = {}
with dpg.font_registry():
    for font in internal_fonts.keys():
        fonts[font] = dpg.add_font(getfont(font),internal_fonts[font][2])


dpg.bind_font(fonts["Standard"])




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

def suspender(sender, data, user_data):
    for job in job_info():
        
        
        cmd = job.command[0].replace("\\","/")

        
        if user_data in cmd: #Already Exists
                
                if job.self != True:
                    if job.status == "RUNNING":
                        execute(f"\\suspend {job.job_id}")
                    else:
                        execute(f"\\resume {job.job_id}")
                    return
        
def open_github(sender, app_data, user_data):
    webbrowser.open("https://"+user_data)

def open_pip(sender, app_data, user_data):
   
        set_clipboard("pip install "+user_data)



def edit_menu(sender, app_data, user_data):
    script_name = user_data["Name"]
    
    def close_it():
        dpg.delete_item(script_name+"_window")


    #Had my boy chat help me on this one
    def overwrite_script():
        if (user_data["Pyjinn"]):

            path = user_data["Dir"] + ".pyj"
        else:
            path = user_data["Dir"] + ".py"

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        new_data = {
            "Name": dpg.get_value(script_name + "_name"),
            "Author": dpg.get_value(script_name + "_author"),
            "MC": str(dpg.get_value(script_name + "_mc")),
            "Version": dpg.get_value(script_name + "_version"),
            "Category": dpg.get_value(script_name + "_category"),
            "Link": dpg.get_value(script_name + "_link"),
            "Description": dpg.get_value(script_name + "_description"),
        }

        output = []
        skipping_description = False
        last_meta_index = -1
        has_docstring = False

        for line in lines:
            stripped = line.strip()

            # --- Strip ALL description blocks completely ---
            if stripped == ">":
                skipping_description = True
                has_docstring = True
                continue

            if stripped == "<":
                skipping_description = False
                continue

            if skipping_description:
                continue

            # --- Detect docstring ---
            if stripped == '"""':
                has_docstring = True
                output.append(line)
                continue

            # --- Replace metadata ---
            replaced = False
            for key in list(new_data.keys()):
                if key == "Description":
                    continue

                tag = f"@{key}:"
                if stripped.startswith(tag):
                    output.append(f"{tag} {new_data.pop(key)}\n")
                    last_meta_index = len(output) - 1
                    has_docstring = True
                    replaced = True
                    break

            if replaced:
                continue

            output.append(line)

            if stripped.startswith("@"):
                last_meta_index = len(output) - 1
                has_docstring = True

        # --------------------------------------------------
        # No existing header → create a new one
        # --------------------------------------------------
        if not has_docstring:
            header = ['"""\n']
            for key, value in new_data.items():
                if key != "Description":
                    header.append(f"@{key}: {value}\n")

            desc = new_data["Description"].strip("\n")
            if desc:
                header.append(">\n")
                header.append(desc + "\n")
                header.append("<\n")

            header.append('"""\n\n')
            output = header + output

        # --------------------------------------------------
        # Existing header → insert missing fields cleanly
        # --------------------------------------------------
        else:
            insert_at = last_meta_index + 1 if last_meta_index >= 0 else 0

            for key, value in list(new_data.items()):
                if key == "Description":
                    continue
                output.insert(insert_at, f"@{key}: {value}\n")
                insert_at += 1

            desc = new_data["Description"].strip("\n")
            if desc:
                output.insert(insert_at, ">\n")
                output.insert(insert_at + 1, desc + "\n")
                output.insert(insert_at + 2, "<\n")

        # --- Write output ---
        if (user_data["Pyjinn"]):

            out_path = user_data["Dir"] + ".pyj"
        else:
            out_path = user_data["Dir"] + ".py"
        with open(out_path, "w", encoding="utf-8") as file:
            file.writelines(output)

        dpg.delete_item("Viewer Window", children_only=True)
        get_scripts()
        generate_scripts()



            #with open()

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
        dpg.add_input_text(default_value=script["Description"].lstrip("\n").rstrip("\n").replace("\n\n","\n"),label="Description \n(CTRL + Enter \nfor new line)",ctrl_enter_for_new_line=True,multiline=True,tag=script_name+"_description")
        dpg.add_button(label="Save",callback=overwrite_script)

script_tags = []
def generate_scripts():
    global script_tags
    script_tags = []
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
                                                        
                                                        dpg.add_button(label="Repo Link",callback= lambda: webbrowser.open(script["Link"].lstrip(" ")))
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

                                                tag = "run_" + script["Dir"].replace("\\","_").replace("/","_").replace(".","_") + str(script["Pyjinn"])
                                                script_tags.append(tag)
                                                dpg.add_checkbox(label="Run", callback=executor,user_data=script["Dir"],tag=tag+"_CB")
                                                dpg.add_checkbox(label="Suspend", callback=suspender,user_data=script["Dir"],tag=tag+"_P")

                                                
                                                with dpg.collapsing_header(label="Script Specific Settings"):
                                                    

                                                    with dpg.table(tag=tag+"_TABLE"):
                                                        dpg.add_table_column(label="Setting")
                                                        dpg.add_table_column(label="Value")
                                                    
                                                    
                                                        #with dpg.table_row():
                                                        #    dpg.add_text("Test")
                                                        #    dpg.add_input_text(default_value="Testing", width=-1)
                                                
                                                #echo(script)

def export_table(sender, app_data, user_data):
    rows = dpg.get_item_children(user_data[0])[1]
    path = config["Data Path Name"]+"/"

    values = []
    data = {}
    for row in rows:
        cells = dpg.get_item_children(row)[1]

        for cell in cells:
            value = dpg.get_value(cell)
            values.append(value)
    
    for i in range(int(len(values)/2)):
        
        key = values[i*2]
        value = values[(i*2)+1]

        try:
            data[key] = ast.literal_eval(value)
        except:
            data[key] = value
    
    with open(path+user_data[1],"w") as f:
        json.dump(data,f)
        
        

last_jobs = ""
def update_monitor():
    global last_jobs
    while True:
        if job_info() != last_jobs:
            
            last_jobs = job_info()
            running = []
            active = []
            paths = []
            for job in job_info():
                tag = "run_" + job.command[0].replace("\\","_").replace("/","_").replace(".","_") + str(".pyj" in job.source)
                running.append(tag)
                if job.status != "RUNNING":
                    active.append(tag)
                paths.append([job.command[0],tag])

            
            for tag in script_tags:
                dpg.set_value(tag+"_CB", tag in running) # EXECUTE
                dpg.set_value(tag+"_P", (tag in active and tag in running)) #PAUSE

        updated_settings = get_settings_for_script()
        for path in scripts:
            
            tag = "run_" + path["Dir"].replace("\\","_").replace("/","_").replace(".","_") + str(path["Pyjinn"])
            
            if path["Dir"]+".json" in updated_settings.keys():
                

                table = tag+"_TABLE"
                dpg.delete_item(table,children_only=True)
                dpg.add_table_column(label="Setting", parent=table)
                dpg.add_table_column(label="Value", parent=table)
                

                for key in updated_settings[path["Dir"]+".json"].keys():
                    with dpg.table_row(parent=table):
                        dpg.add_text(key)
                        dpg.add_input_text(default_value=updated_settings[path["Dir"]+".json"][key],width=-1,callback=export_table,on_enter=True,user_data=[table,path["Dir"]+".json"])
                
                
                

        sleep(MONITOR_DELAY)
        




def format_report():
    info = version_info()
    report = "Autogenerated Debug Info:\n"
    report += "MC Version: "+info.minecraft+"\n"
    report += "Pyjinn Version: "+info.pyjinn+"\n"
    try:
        report += "MSP Version: "+msp_ver+"\n"
    except:
        report += "MSP Version: Not Present\n"
    report += "Mod Loader: "+info.mod_loader+"\n"
    
    report += "Mods:\n```"
    for mod in mods:
        report += mod+", "
    report.removesuffix(", ")
    report += "```"
    
    set_clipboard(report)

def toggle_top(sender, app_data, user_data):
    #echo(app_data)
    if user_data == "Always On Top":
        dpg.set_viewport_always_top(app_data)
    config[user_data] = app_data
    save_settings()

def text_setting(sender, app_data, user_data):

    try:
        data = ast.literal_eval(app_data)
    except:
        data = app_data

    
    config[user_data] = data
    if user_data == "Hotload Delay":
        global MONITOR_DELAY
        MONITOR_DELAY = data
    save_settings()

def float_setting(sender, app_data, user_data):
    try:
        data = ast.literal_eval(app_data)
    except:
        data = app_data

    data = round(data*100)/100
    
    config[user_data] = data
    if user_data == "Hotload Delay":
        global MONITOR_DELAY
        MONITOR_DELAY = data
    save_settings()

mods = []
for mod in os.listdir("../mods"):
    if mod.endswith(".jar"):
        mods.append(mod.removesuffix(".jar"))


def settings_tab():
    with dpg.collapsing_header(label="Debug Info"):
                    
                    info = version_info()
                    if not MSP:
                        dpg.add_text("Minescript Plus: "+"Not Present.")
                    else:
                        dpg.add_text("Minescript Plus: "+msp_ver)



                    dpg.add_text("MC Version: "+info.minecraft)

                    dpg.add_text("Minescript Version: "+info.minescript)

                    dpg.add_text("Mod Loader: "+info.mod_loader)
                    
                    dpg.add_text("Pyjinn Version: "+info.pyjinn)

                    dpg.add_text("OS: "+info.os_name)

                    with dpg.tree_node(label="Mods"):
                        for mod in mods:
                            dpg.add_text(mod)

                    dpg.add_button(label="Copy Info",callback=format_report)
    
    
    with dpg.tree_node(label="Window Settings"):
        dpg.add_checkbox(label="Always On Top",callback=toggle_top,default_value=config["Always On Top"],user_data="Always On Top") #
        dpg.add_checkbox(label="Show Only With Screens",callback=toggle_top,default_value=config["Hide Except Screens"],user_data="Hide Except Screens")
        dpg.add_checkbox(label="Only Show With Inventory Screens (Requires setting above)",callback=toggle_top,default_value=config["Inventory Screens Only"],user_data="Inventory Screens Only")
    
    with dpg.tree_node(label="Performance"):
        dpg.add_text("All settings here require a restart of Launcher / Lib_launcher scripts.")
        dpg.add_input_double(label="Hotloading Delay Interval (Effects lib_launcher API responsiveness)",callback=float_setting,default_value=config["Hotload Delay"],user_data="Hotload Delay",width=100)
        dpg.add_input_double(label="lib_launcher Minimum Delay Interval",callback=float_setting,default_value=config["Lib Launcher Min Time"],user_data="Lib Launcher Min Time",width=100)
    """
    dpg.add_text("SETTINGS PAST HERE NOT IMPLEMENTED")
    with dpg.tree_node(label="Auto Updates"):
        dpg.add_text("These are just placeholders, nothing does anything yet :)")
        dpg.add_checkbox(label="Automatically check for updates")
        dpg.add_input_int(label="Automatic update interval (Days)",width=100)

        dpg.add_checkbox(label="Allow Scripts to Auto-Update")
        dpg.add_input_int(label="Auto Update Interval (Days)")

    #with dpg.tree_node(label=)
    """

def integration_tab():
    pass




def import_tab():
    dpg.add_text("Import Singular Script")
    dpg.add_input_text(label="Import from github",default_value="https://github.com/R4z0rX/minescript-scripts/blob/main/Minescript-Plus/minescript_plus.py",callback=import_from_github,on_enter=True,user_data="")

def kill_notif(sender, app_data, user_data):
    dpg.delete_item(user_data)
def make_notification(title,content,tag=None):
    
    title = title + f" ({datetime.datetime.now().strftime("%H:%M")})"
    if tag is None:
        tag = title
    with dpg.child_window(label=title,parent="Notifications",height=150, tag=tag):
        with dpg.group(horizontal=False):
            t = dpg.add_text(title,indent=20)
            dpg.bind_item_font(t, fonts["Bold"])
            dpg.add_separator()
            t = dpg.add_text(content,indent=20)
            dpg.bind_item_font(t, fonts["Notification"])

            with dpg.group(horizontal=True):
                dpg.add_button(label="OK",callback=kill_notif,user_data=tag,indent=20)

                #dpg.add_button(label="Hi!!")
        


with dpg.window(label="Launcher", width=600,height=300, tag="Main"):
    
    with dpg.child_window(label="Bar",tag="Bar Window"):
        
        dpg.add_text("Notifications",tag="Notifications Label")
        with dpg.child_window(label="Notifications",height=200,tag="Notifications"):
            pass
        #make_notification("Welcome!","Welcome to the GUI launcher!\nI hope you have fun!")
        #make_notification("Welcome!!","Welcome to the GUI launcher!\nI hope you have fun!")
        #make_notification("Welcome!!!","Welcome to the GUI launcher!\nI hope you have fun!")
        with dpg.tab_bar():
            

            with dpg.tab(label="Viewer",tag="Viewer Window"):
                generate_scripts()
            

            with dpg.tab(label="Script Integrations",tag = "Integrations"):
                integration_tab()
            
            with dpg.tab(label="Settings",tag="Settings"):
                settings_tab()

            with dpg.tab(label="Import Scripts",tag="Imports"):
                import_tab()
            

def setting_thread():
    last_update = os.path.getmtime("launcher_config.json")
    while True:
        if last_update != os.path.getmtime("launcher_config.json"):
            last_update = os.path.getmtime("launcher_config.json")
            readcfg()
        time.sleep(0.4)
                
#threading.Thread(target=setting_thread,daemon=True).start()
                
def game_montoring():
    
    with render_loop:
        time.sleep(0.1)
        last_viewport = dpg.get_viewport_pos()

        while True:
            if config["Hide Except Screens"] and config["Always On Top"]:
                name = str(screen_name())
                
                if name == "None" or (config["Inventory Screens Only"] and (not "Crafting" in name and not "Creative" in name)):
                    dpg.set_viewport_pos((0,-9999))
                else:
                    if dpg.get_viewport_pos()[1] < -999:
                        dpg.set_viewport_pos(last_viewport)

                    last_viewport = dpg.get_viewport_pos()




dpg.set_primary_window("Main",True)

dpg.setup_dearpygui()
dpg.show_viewport()

dpg.set_viewport_always_top(config["Always On Top"])

def keep_awake():
    with EventQueue() as event_queue:
        event_queue.register_world_listener()
        while True:
            sleep(500)


def notification_manager():
    while True:
        try: #idrk but it hates exiting and this fixes it
            sleep(0.1)
            children = False
            group = dpg.get_item_children("Notifications")
            for item in (group).keys():
                if group[item] != []:
                    children = True

            if children:
                dpg.show_item("Notifications")
                dpg.show_item("Notifications Label")
            else:
                dpg.hide_item("Notifications")
                dpg.hide_item("Notifications Label")

        except:
            pass

window = True
threading.Thread(target=keep_awake, daemon=True).start()
threading.Thread(target=game_montoring,daemon=True).start()
threading.Thread(target=update_monitor,daemon=True).start()
threading.Thread(target=notification_manager,daemon=True).start()


dpg.start_dearpygui()
dpg.destroy_context()

