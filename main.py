#The main start path of the CLI program
#yes this is for some reason gonna be supported on linux, should it? No, do we ball though? Yes

#Developer information:
#If you make a commit request I might look at it, and might aprove it.
#If you wanna make linux support for some reason go ahead.
#Feel free to improve my sucky code/optimize it if possible.
#Please add GPT.
#This is free and open source since im tired of corps making this easy software $20, maybe ill make a data recovery tool to destroy DiskDrill.
#If you do end up copying this repo, I beg to be credited, not enforced though.

#TODO:
#Add GUI
#Add GPT partition support
#Add full EXT filesystem support
#Add Btrfs support
#Add every unsupported partition (thats not in windows, leave out linux for some other person if they wanna add this linux for some reason).
#Add user decryption.
#Add saving files to windows




#fish!

import ctypes, os
import subprocess
from Libraries.ExtryError import *
import Libraries.Packages as Packages
from Libraries.menu.SelectionMenu import SelectionMenu
from DriveOperations.drive_operations import *
import sys

def elevate():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    exit()

def is_admin():
    #Taken from https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    return is_admin


if __name__ == "__main__":
    if not is_admin():
        elevate()
    

    #install and check python packages
    if not Packages.Install_Packages(): print("Error while installing packages. Please check log for more information.")
    print("Done with the setup...")

    

    SupportedDrives=DetectEXTFileSystems()
    #print(f"Found {len(SupportedDrives)} supported drive(s).")
    DriveNames=[]
    for drive in SupportedDrives:
        DriveNames.append(f"Drive: {drive[4]}, partition {drive[5]}")
        #print()
        #driveSizeInfo=ConvertSize(drive[1])
        #print(f"Drive {drive[4]}, partition {drive[5]}")
        #this was just extra info, please make it shorter
        #print(f"Size: {math.floor(driveSizeInfo[0]*100)/100}{driveSizeInfo[1]}")

    MENU=SelectionMenu()
    MENU.create_UI(DriveNames)
    while True:
        MENU.update()