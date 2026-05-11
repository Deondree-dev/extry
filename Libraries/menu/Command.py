from Libraries.filesystems.filesystem import filesystem
import traceback
import os

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
        self.commandList["copy"]=self.Copy

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

    def Copy(self, ArgumentVector:list):
        try:
            LinuxPath:str=ArgumentVector[0]
            WindowsPath:str=ArgumentVector[1]
            WindowsPathVector=WindowsPath.split("/")
            #just making it better so the user doesn't have to manually make the folders
            os.makedirs(WindowsPath.removesuffix(WindowsPathVector[-1]), exist_ok=True)

            WindowsFile=open(WindowsPath, "wb")

            fileBytes, filetype = self.fs.readFile(LinuxPath)
            
            if filetype!=1:
                print(f"Linux File: {LinuxPath} doesn't exist.")
                return
            if not WindowsFile.writable():
                print(f"Windows File: {WindowsPath} isn't writable right now.")
                return
            
            WindowsFile.write(fileBytes)
            print(f"Successfully wrote: {fileBytes} to {WindowsPath}")
            WindowsFile.close()
        except IndexError:
            print("Usage: copy <FromLinuxFilePath> <ToWindowsFilePath>")
