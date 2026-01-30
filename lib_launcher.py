import os
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
    "Confined":False
}

def _readcfg():
    global config
    try:

        with open("launcher_config.json", "x") as file:
            json.dump(default_config,file)
        config = default_config
    except FileExistsError:

        with open("launcher_config.json", "r") as file:
            config = json.load(file)
        
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
        with open(FROM+".json","x") as file:
            json.dump(defaults,file)
        return defaults
    except FileExistsError:
        
        with open(FROM+".json","r") as file:
            to_use = json.load(file)

        for data in defaults.keys():
            if not data in to_use:
                to_use[data] = defaults[data]
        
        with open(FROM+".json","w") as file:
            json.dump(to_use,file)
        return to_use

def read():
    FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")
    
    with open(FROM+".json","r") as file:
        return json.load(file)

def write(info):
    FROM = inspect.stack()[1].filename.rpartition("\\")[-1].removesuffix(".py")

    with open(FROM+".json","w") as file:
        json.dump(info,file)

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

    while True:
        
        if last_modified != os.path.getmtime(FROM+".json"):
            

            data = ""
            with open(FROM+".json","r") as file:
                data = json.load(file)
            callback(data)
            last_modified = os.path.getmtime(FROM+".json")
        else:
            sleep(interval)
