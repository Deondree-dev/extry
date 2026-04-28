#Allows a point of entry for the drive

#import wmi; please don't judge the code, it may just be temp, maybe...
try:
    import wmi
except ImportError:
    print("Could not import the 'wmi' module; installing it now...")
    try:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", 'wmi'])
    except ImportError:
        print("Could not import the 'subproccess' or 'sys' modules; please verify if it exists, or reinstall python.")
        exit()
    try:
        import wmi
    except ImportError:
        print("Could not import the 'wmi' module; failed to install. Please manually install the package using 'python -m pip install wmi")
        exit()

import math
from Libraries.EXT4.ReadHeader import *

def ConvertSize(size:int)->list[int,str]:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return size, unit
        size /= 1024


def detect_drives()->list:
    drives=[]
    for i, drive in enumerate(wmi.WMI().Win32_DiskDrive()):
        drives.append({"address":drive.DeviceID, "name":drive.Model, "size":drive.Size, "serial":drive.SerialNumber.strip()})
    
    return drives

def getPartitionType(address:str)->str:
    Byte=open(address, "rb").read(451)[450]
    return "gpt" if Byte == 0xEE else "mbr"

def getMBRPartitionsInfo(address:str)->list[bytes]:
    partitions=[]
    BYTES=open(address,"rb").read(512)[446:510]
    for i in range(0,4):
        #appends partition from start, at 446+16*i, through end, start+16
        start=16*i
        partition=BYTES[start:start+16]
        if not len(partition.replace(b'\x00',b"")) == 0:
            partitions.append(partition)
    return partitions

#[IsEXT4, sizeinbyte, startbyte, endbyte]

def getMBRPartitionInfo(address:str, partitionInfo:bytes)->list[bool, int, int, int]:
    
    #size of partition
    sizeinLBA=int.from_bytes(partitionInfo[12:16], "little")
    sizeInBytes=sizeinLBA*512
    
    startLBA=int.from_bytes(partitionInfo[8:12], "little")
    startByte=startLBA*512
    endByte=sizeInBytes+startByte

    #print(f"Partition: {startByte}->{endByte}")
    #print(f"Reading: {startByte}->{startByte+512}")
    try:
        return [IsEXT4(address, startByte, endByte), sizeInBytes, startByte, endByte]
    except OSError as e:
        print(f"Operating System error: {e}")
    
    return [False, sizeInBytes, startByte, endByte]



def getGPTPartitionsBytes(address:str)->list:...

def DetectEXTFileSystems()->list:
    SpecialFilesystems=[]
    #holly bird nest bro, please... someone... FIX THIS MONSTER
    for drive in detect_drives(): #- im a monster :(
        #drive specific code:
        #print(f"{drive["name"]}: {getPartitionType(drive["address"])}")
        if getPartitionType(drive["address"]) == "mbr":
            partitions=getMBRPartitionsInfo(drive["address"])
            for i, partitionInfo in enumerate(partitions):
                partitionInfomation=getMBRPartitionInfo(drive["address"], partitionInfo)
                if partitionInfomation[0]:
                    partitionInfomation.append(drive["name"])
                    partitionInfomation.append(i+1)
                    partitionInfomation.append(drive["address"])
                    SpecialFilesystems.append(partitionInfomation)

    return SpecialFilesystems