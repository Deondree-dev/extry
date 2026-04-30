#defines a selection menu for the user to navigate the UI cleanly

from Libraries.menu.UI import UI
from DriveOperations.drive_operations import DetectEXTFileSystems
from Libraries.EXT4.filesystem import ext4
from Libraries.filesystems.filesystem import *

class SelectionMenu(UI):
    def __init__(self):
        super().__init__()
        self.DriveInt:int=-1
        self.Drives:list=[]
        print("Pick option: ")
    
    def __getIntInput(self,length)->int:
        gotInt:bool=False

        while not gotInt:
            try:
                integer=(input(f"Please select a number. [0-{length-1}] "))
                if integer=="exit": return -1
                if int(integer)>length-1 or int(integer)<0: raise KeyError()
                return int(integer)
            except ValueError:
                print("Not an Integer; please use only integers. Type: \"exit\" to exit.")
            except KeyError:
                print("Not in list; please select one in list. Type: \"exit\" to exit.")
            except Exception as e:
                print(f"Got unexpected error, please report this to the github issues. {e}")

    def EnterDriveSelection(self):
        for i, drive in enumerate(self.Drives):
            print(f"{i}: Drive: '{drive[4]}' partition {drive[5]}")
        
        drive=self.__getIntInput(len(self.Drives))
        self.DriveInt=drive

    

    def EnterfilesystemExplorer(self, once=False):
        try:
            Drive:list=self.Drives[self.DriveInt]

        except IndexError:
            if not once:
                print("Cant find the drive, maybe it got unplugged? Retrying once.")
                self.EnterfilesystemExplorer(once=True)
            else:
                print("Plug in the drive and try again.")
                return
            
        fs:filesystem = ext4(Drive[6], Drive[2], Drive[3])
        
        inDirectoryViewer=True
        currentDir="/"
        dirBlock={}
        
        inode = fs.GetInode(2)
        Entries=fs.ParseExtentTree(inode[0x28:0x28+60])
        for blockNum, __ in Entries:
            dirBlock=fs.ParseBlockDirectories(blockNum)
        
        printDirblock=True
        
        while inDirectoryViewer:
            command=input(">>> ")
            #commands
            if command=="cwd":
                print(currentDir)
            
            elif command.startswith("ls "):
                printDirblock=False
                path=command.removeprefix("ls ")
                if not path.startswith("/"):
                    path=currentDir+path
                
                paths, filetype = fs.read(path)
                
                match (filetype):
                    case 0:
                        print("File/Folder does not exist")
                    case 1:
                        print(paths["File"])
                    case 2:
                        for pathName in paths:
                            print(f"{pathName} file type: {paths[pathName][4]}")
            
            elif command.startswith("cd "):
                path=command.removeprefix("cd ")
                currentDir+=f"{path}/"
                paths, filetype = fs.readPath(currentDir)
                
                match (filetype):
                    case 0:
                        print("File/Folder does not exist")
                    case 1:
                        print("Cant change directory to a file.")
                    case 2:
                        for pathName in paths:
                            print(f"{pathName} file type: {paths[pathName][4]}")

            elif command.startswith("cat "):
                path=command.removeprefix("cat ")
                if not path.startswith("/"):
                    path=currentDir+path
                fileBytes, filetype = fs.readFile(path)
                if filetype!=1:
                    print("File doesn't exist.")
                    continue
                print(fileBytes)
            

    def update(self):
        self.Drives=DetectEXTFileSystems()
        if not self.DriveInt==-1:
            print()
            print(self.create_UI(["Select another drive", "Open filesystem", "Exit"]))
            UserInput=input(">>> ")
            match (UserInput):
                case "1":
                    self.EnterDriveSelection()
                case "2":
                    self.EnterfilesystemExplorer()
                case "3":
                    exit()
                case __:
                    print("Unknown operation.")
        else:
            print()
            print(self.create_UI(["List drives", "Select a drive", "Exit"]))
            UserInput=input(">>> ")
            match (UserInput):
                case "1":
                    for i, drive in enumerate(self.Drives):
                        print(f"{i}: Drive: '{drive[4]}' partition {drive[5]}")
                case "2":
                    self.EnterDriveSelection()
                case "3":
                    exit()
                case __:
                    print("Unknown operation.")
        
        
        super().update()
