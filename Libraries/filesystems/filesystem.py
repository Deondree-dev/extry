#This is so I can add dynamic filesystems and its easier to know what something does.


class filesystem:
    
    def __init__(self, DriveAddress:str, PartitionStartByte:int, PartitionEndByte:int):
        self.DriveAddress=DriveAddress
        self.PartitionStartByte=PartitionStartByte
        self.PartitionEndByte=PartitionEndByte
        self._len16=2
        self._len32=4

    def ParseBlockDirectories(self, path:str)->str:...

    def readPath(self, AbsolutePath:str)->tuple[list, int]:...

    def readFile(self, path:str)->bytes:...

    def rewrite(self, path:str, file:str, data:bytes)->bool:...

    def write(self, path:str, file:str, AddData:bytes)->bool:...