from filesystems.filesystem import filesystem 

class debug:
    def __init__(self, fs:filesystem):
        pass
    def HandleDebug(self, input:str):
        if input.lower().startswith("debug "):
            input=input.lower().removeprefix("debug ")
