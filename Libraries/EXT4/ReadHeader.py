
def ScanForExt4(Head:bytes)->bool:
    return Head[0x38]==83 and Head[57]==239


def IsEXT4(address:str, startByte:int, endByte:int)->bool:
    drive=open(address, "rb")
    drive.seek(startByte+2048)
    HEAD=drive.read(2048)
    drive.close()
    return ScanForExt4(HEAD)