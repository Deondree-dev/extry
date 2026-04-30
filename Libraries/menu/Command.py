from Libraries.filesystems.filesystem import filesystem

class console:
    def __init__(self, fs:filesystem):
        self.commandList:dict[function]
        self.fs=fs
    
    def RegisterCommands(self):
        self.commandList["ls"]=self.ListDirectory

    def FetchCommand(self, command:str):
        ArgumentVector=command.split(" ")
        if ArgumentVector[0] in self.commandList:
            self.commandList[ArgumentVector[0]](self,ArgumentVector[0:])

    def ListDirectory(self, ArgumentVector:list):
        path=ArgumentVector[0]
        if not path.startswith("/"):
            path=currentDir+path
                
        paths, filetype = self.fs.read(path)
                
        match (filetype):
            case 0:
                print("File/Folder does not exist")
            case 1:
                print(paths["File"])
            case 2:
                for pathName in paths:
                    print(f"{pathName} file type: {paths[pathName][4]}")
