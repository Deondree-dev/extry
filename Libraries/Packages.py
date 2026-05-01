#this just installs needed packages


from Libraries.ExtryError import *
from importlib import util
import subprocess
import sys

def download_package(package:str)->bool:
    print (f"Installing: {package}")
    try:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except ImportError:
        print ("Could not import the 'subproccess' or 'sys' modules; please verify if it exists, or reinstall python.")
        return False
    except subprocess.CalledProcessError:
        print ("Installing pip")
        subprocess.check_call(["python3", "get_pip.py"])
        
    return True

def download_package_batch(batch:list)->bool:
    if len(batch) == 0: return True
    success=True
    print ("Installing needed packages.")
    print ("Please wait.")
    for package in batch:
        if not download_package(package): success=False 
    
    return success
        

def Install_Packages()->bool:
    success=False
    try:
        if not getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            requiredPackages=open("./requirements.txt", "r").read().split("\n")
            notInstalled=[]
            for package in requiredPackages:
                notInstalled.append(package) if util.find_spec(package) is None else None
            success=download_package_batch(notInstalled)
        else:
            success=True
    except FileNotFoundError as e:
        print("Couldn't find file \"requirements.txt\". Please make sure your running from root directory. \n(WARNING) running without installing the required packages.")

    return success