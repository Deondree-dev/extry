from Libraries.filesystems.filesystem import filesystem
import traceback

class console:
    def __init__(self, fs:filesystem):
        self.commandList:dict[function]={}
        self.fs=fs
        self.AbsolutecurrentDir="/"
        self.RegisterCommands()
    
    def RegisterCommands(self):
        self.commandList["ls"]=self.ListDirectory
        self.commandList["cd"]=self.ChangeDirectory
        self.commandList["cwd"]=self.CurrentWorkingDirectory
        self.commandList["cat"]=self.Concatenate

    def FetchCommand(self, command:str):
        ArgumentVector=command.split(" ")
        if ArgumentVector[0] in self.commandList:
            try:
                self.commandList[ArgumentVector[0]](ArgumentVector[1:])
            except Exception as e:
                print(f"Got error while executing command: {ArgumentVector[0]}\n{e}\nStack Trace:")
                traceback.print_exc()

    def CurrentWorkingDirectory(self, ArgumentVector:list):
        if len(ArgumentVector)>1:
            print("Incorrect usage.\nE.x.: cwd")
            return
        print(self.AbsolutecurrentDir)

    def ListDirectory(self, ArgumentVector:list):
        if len(ArgumentVector)<=0:
            ArgumentVector=[self.AbsolutecurrentDir]
        path:str=ArgumentVector[0]
        if not path.startswith("/"):
            path=self.AbsolutecurrentDir+path
                
        paths, filetype = self.fs.readPath(path)
        print(filetype)
        match (filetype):
            case 0:
                print("File/Folder does not exist")
            case 1:
                print(paths["File"])
            case 2:
                for pathName in paths:
                    print(f"{pathName} file type: {paths[pathName][4]}")

    def ChangeDirectory(self, ArgumentVector:list):
        path:str=ArgumentVector[0]
        if not path.startswith("/"):
            self.AbsolutecurrentDir=self.AbsolutecurrentDir+path+"/"
        else:
            self.AbsolutecurrentDir=path

    def Concatenate(self, ArgumentVector:list):
        path=ArgumentVector[0]
        if not path.startswith("/"):
            path=self.AbsolutecurrentDir+"/"+path
        fileBytes, filetype = self.fs.readFile(path)
        if filetype!=1:
            print(f"File: {path} doesn't exist.")
        print(fileBytes)