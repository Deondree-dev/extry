
def getPartitionType(address:str)->str:
    Byte=open(address, "rb").read(450)[450]
    return "gpt" if Byte == 0xEE else "mbr"