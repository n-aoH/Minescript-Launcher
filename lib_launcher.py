

"""
@Name: Lib Launcher
@Author: @No
@MC: Tested on 1.21.11. Works on all versions.
@Version: 4
@Category: INFO
@Link: https://github.com/n-aoH/Minescript-Launcher/blob/main/lib_launcher.py

>
The GUI Launcher's API. Happy programming!
<
"""

py = False
try:
    Minecraft = JavaClass("net.minecraft.client.Minecraft") #type: ignore
    
except NameError:
    py = True

default_notif = {
    "Title":"Untitled",
    "Content":"Hello, World!",
    "Type":"Text"
}

if py:

    import os
    import time
    import inspect
    import json
    from time import sleep
    import threading


    try:
        os.chdir("minescript")
    except:
        pass

    default_config = {
        "Path":"launcher",
        "Data Path Name":"launcher data",
        "Confined":False,
        "Lib Launcher Min Time":0.1
    }

    def _readcfg():
        global config
        try:

            file = open("launcher_config.json", "x")
            
            json.dump(default_config,file)
            config = default_config

            file.close()
        except FileExistsError:

            file = open("launcher_config.json", "r")
            
            config = default_config
            new_cfg = json.load(file)
            
            for key in new_cfg.keys():
                config[key] = new_cfg[key]
            

            file.close()

    _readcfg()    

    NAME = config["Path"]
    CONFINED = config["Confined"]
    DATA_PATH = config["Data Path Name"]

    if CONFINED:
        os.chdir(NAME)

    # Get to the right dir
    try:
        os.chdir(DATA_PATH)
    except:
        os.mkdir(DATA_PATH)
        os.chdir(DATA_PATH)




    def initialize(defaults):
        """
        Creates a JSON dict 


        """
        FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")

        try:
            file = open(FROM+".json","x")
            
            json.dump(defaults,file)

            file.close()
            return defaults
        except FileExistsError:
            
            file = open(FROM+".json","r")
            
            to_use = json.load(file)

            file.close()

            for data in defaults.keys():
                if not data in to_use:
                    to_use[data] = defaults[data]

            file = open(FROM+".json","w")
            
            json.dump(to_use,file)

            file.close()

            return to_use

    def read():
        FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")

        file = open(FROM+".json","r")

        json = json.load(file)

        file.close()
        return json

    def write(info):
        FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")

        file = open(FROM+".json","w")
        
        json.dump(info,file)
        
        file.close()

    def monitor(callback, interval=1.0):
        FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")
        thread = threading.Thread(
            target=_monitoring,
            args=(FROM,callback,interval),
            daemon=True
        )
        thread.start()

    def _monitoring(FROM,callback,interval):
        last_modified = os.path.getmtime(FROM+".json")

        sleeptime = config["Lib Launcher Min Time"]
        if interval > sleeptime:
            sleeptime = interval

        while True:

            if last_modified != os.path.getmtime(FROM+".json"):


                data = ""

                file = open(FROM+".json","r")
                
                data = json.load(file)

                file.close()

                callback(data)
                last_modified = os.path.getmtime(FROM+".json")
            else:
                sleep(sleeptime)
    

    notif_count = 0
    def make_notification(type="Text",title="Untitled",content="Body Content"):
        global notif_count
        notif_count += 1
        FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")
        filename = FROM+"_"+str(notif_count)+"_"+str(int(time.time()))+".notif"
        path = filename

        data = default_notif

        data["Type"] = type
        data["Title"] = title
        data["Content"] = content
        with open(path, "w") as f:
            json.dump(data, f, indent=2)


else:
    print("Under development :) Pyjinn coming later")
