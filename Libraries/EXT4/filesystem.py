import io
from Libraries.filesystems.filesystem import *
from DriveOperations.drive_operations import *
import sys
from Libraries.ExtryError import *

#creds:
#https://archive.kernel.org/oldwiki/ext4.wiki.kernel.org/index.php/Ext4_Disk_Layout.html
#https://github.com/torvalds/linux/blob/master/fs/ext4/ext4.h (WHAT??? WHO COULD HAVE GUESSED????)
#https://www.kernel.org/doc/html/latest/filesystems/ext4/journal.html#super-block
#and the online stackoverflow post that helped me debug block size and number of blocks (im not going to find them)


class ext4(filesystem):
    
    def __init__(self, DriveAddress:str, PartitionStartByte:int, PartitionEndByte:int):
        super().__init__(DriveAddress, PartitionStartByte, PartitionEndByte)
        print(self.DriveAddress)
        self.__SETUP_DRIVE_()

    def __SETUP_DRIVE_(self):
        #i make sure to define what every thing is class-wise so nothing is changed
        self.Drive:io.BufferedReader=open(self.DriveAddress, "rb")
        self.SeekOffset=2048
        self.Drive.seek(self.PartitionStartByte+self.SeekOffset) #set to the partitions start byte and plus 2048 to avoid seeking though boot code or anything else
        
        self.DriveHeaderInfo:bytes=self.Drive.read(2048) #the superblock thingy
        
        #inodes
        self.NumberofInodes:int=int.from_bytes(self.DriveHeaderInfo[0x00:0x03], "little")
        self.InodesPerGroup:int=int.from_bytes(self.DriveHeaderInfo[0x28:0x2c], "little")
        self.InodeSize: int = int.from_bytes(self.DriveHeaderInfo[0x58:0x5A], "little")



        #blocks
        self.NumberofBlockslo:int=int.from_bytes(self.DriveHeaderInfo[0x04:0x08], "little")
        self.NumberofBlockshi:int=int.from_bytes(self.DriveHeaderInfo[0x150:0x154], "little")
        
        self.BlockSize:int = 1024 << int.from_bytes(self.DriveHeaderInfo[0x18:0x1C], "little")




        FeatureIncompat:int = int.from_bytes(self.DriveHeaderInfo[0x60:0x64], "little")
        self.is_64bit:bool = bool(FeatureIncompat & 0x80)
        if self.is_64bit:
            self.TotalNumberofBlocks:int = (self.NumberofBlockshi << 32) | self.NumberofBlockslo
        else:
            self.TotalNumberofBlocks:int = self.NumberofBlockslo
        
        #encryption
        Encryption=(self.DriveHeaderInfo[0x254])
        print(Encryption)




    

    def GetBlock(self, block: int) -> bytes:
        target = self.PartitionStartByte + 1024 + (self.BlockSize * block)
        try:
            with open(self.DriveAddress, "rb") as f:
                f.seek(target)
                return f.read(self.BlockSize)
        except PermissionError:
            print("Woah, we dont have permission to read that. Please report the issue to the github along with this:")
            print(f"Block Number: {block}. Size of drive: {self.PartitionStartByte-self.PartitionEndByte}")
            print("If you feel that you could fix the error, send the fix on the github and I'll look into it!")
    
    def ParseExtentTree(self, tree:bytes)->list:
        Magic=int.from_bytes(tree[0x0:0x0+self._len16], "little")
        NumberOfEntries=int.from_bytes(tree[0x2:0x2+self._len16], "little")
        MAXENTRIES=int.from_bytes(tree[0x4:0x4+self._len16], "little")
        Depth=int.from_bytes(tree[0x6:0x6+self._len16], "little")

        #keep entries
        Entries=[]

        def handle_internal(Entry):
            leaf_lo=int.from_bytes(Entry[0x4:0x4+self._len32], "little")
            leaf_hi=int.from_bytes(Entry[0x8:0x8+self._len16], "little")

            return leaf_lo, leaf_hi
        
        def handle_leaf(Entry):
            length=int.from_bytes(Entry[0x4:0x4+self._len16], "little")
            leaf_hi=int.from_bytes(Entry[0x6:0x6+self._len16], "little")
            leaf_lo=int.from_bytes(Entry[0x8:0x8+self._len32], "little")

            return leaf_lo, leaf_hi, length

        for i in range(0, NumberOfEntries):
            Entry = tree[0xC+(i * 12):0xC+12+(i * 12)] # get the entry
            if Depth==0:
                leaf_lo, leaf_hi, length=handle_leaf(Entry)
                BlockNum=(leaf_hi << 32) | leaf_lo
                Entries.append([BlockNum , length])
            elif Depth>0:
                leaf_lo, leaf_hi=handle_internal(Entry)
                BlockNum=(leaf_hi << 32) | leaf_lo
                entries=self.ParseExtentTree(self.GetBlock(BlockNum))
                Entries.extend(entries)
            else:
                raise UnboundLocalError(f"Depth is not 0 or >0 in ParseExtentTree(self, tree:bytes). Depth: {Depth}")
        
        return Entries

    def GetBlockInodeTable(self, group: int) -> tuple[int, int]:
        desc_size = 64
        desc_offset = group * desc_size
        block_num = 1 + (desc_offset // self.BlockSize)
        offset_within_block = desc_offset % self.BlockSize
        desc_block = self.GetBlock(block_num)
        desc = desc_block[offset_within_block:]
        inode_table_lo = int.from_bytes(desc[0x08:0x0C], "little")
        inode_table_hi = int.from_bytes(desc[0x28:0x2C], "little")
        return inode_table_lo, inode_table_hi

    def GetInode(self, inode: int) -> bytes:
        block_group = (inode - 1) // self.InodesPerGroup
        index = (inode - 1) % self.InodesPerGroup

        inode_table_lo, inode_table_hi = self.GetBlockInodeTable(block_group)
        inode_table = (inode_table_hi << 32) | inode_table_lo

        block_offset = (index * self.InodeSize) // self.BlockSize
        index_within_block = (index * self.InodeSize) % self.BlockSize

        block_data = self.GetBlock(inode_table + block_offset)
        return block_data[index_within_block:index_within_block + self.InodeSize]

    def GetBlockNumberByInode(self, inode: int, Magic=0xF30A, ignoreMagic=False) -> int:
        inode_bytes = self.GetInode(inode)
        magic = int.from_bytes(inode_bytes[0x28:0x2A], "little")
        if magic != Magic and not ignoreMagic:
            raise ValueError(f"Does not match Magic: {hex(magic)}")
        ee_start_hi = int.from_bytes(inode_bytes[0x3A:0x3C], "little")
        ee_start_lo = int.from_bytes(inode_bytes[0x3C:0x40], "little")
        return (ee_start_hi << 32) | ee_start_lo

    def GetRootInodeTable(self) -> int:
        Block: bytes = self.GetBlock(1)
        bg_inode_table_lo = int.from_bytes(Block[0x08:0x0C], "little")
        bg_inode_table_hi = int.from_bytes(Block[0x28:0x2C], "little")
        return (bg_inode_table_hi << 32) | bg_inode_table_lo

    def GetRootDir(self)->int:
        InodeTable = self.GetBlock(self.GetRootInodeTable())
        inode = InodeTable[256:512]
        ee_start_hi = int.from_bytes(inode[0x3A:0x3C], "little")
        ee_start_lo = int.from_bytes(inode[0x3C:0x40], "little")
        ee_start = (ee_start_hi << 32) | ee_start_lo
        return ee_start
    
    def ParseBlockDirectories(self, block:int)->list[int,int,int,int,str]:
        BlockData:bytes=self.GetBlock(block)
        more=True
        offset=0
        directories=[]
        try:
            while more:
                inode:int=int.from_bytes(BlockData[0x0+offset:0x4+offset], "little")
                rec_len:int=int.from_bytes(BlockData[0x4+offset:0x6+offset], "little")
                namelength:int=BlockData[0x6+offset]
                filetype:int=BlockData[0x7+offset]
                name:str=BlockData[0x8+offset:0x8+offset+namelength].decode(encoding="utf-8")
                directories.append([inode,rec_len,namelength,filetype,name])
                offset+=rec_len

                if rec_len==0:
                    more=False
                    break

                if offset>=len(BlockData):
                    more=False
                    break
        except UnicodeDecodeError:
            print("Got a UnicodeDecodeError, not a directory.")
            return []
            
        return directories
        
    def _ParseBlockDirectories_(self, block:int)->dict[str]:
        BlockData:bytes=self.GetBlock(block)
        more=True
        offset=0
        directories={}
        try:
            while more:
                if offset>=len(BlockData):
                    more=False
                    break
                inode:int=int.from_bytes(BlockData[0x0+offset:0x4+offset], "little")
                rec_len:int=int.from_bytes(BlockData[0x4+offset:0x6+offset], "little")
                namelength:int=BlockData[0x6+offset]
                filetype:int=BlockData[0x7+offset]
                name:str=BlockData[0x8+offset:0x8+offset+namelength].decode(encoding="utf-8")
                
                offset+=rec_len

                if inode==0:
                    continue #skip inode 0

                directories[name]=[False,inode,rec_len,namelength,filetype,name]
                if rec_len==0:
                    more=False
                    break

                if offset>=len(BlockData):
                    more=False
                    break
        except UnicodeDecodeError as e:
            print(f"Got a UnicodeDecodeError, not a directory. {e}")
            return {}
            
        return directories

    def _ParseBlockDirectoriesBytes_(self, block:int, ThrowErrorsBack=False)->dict[str]:
        BlockData:bytes=self.GetBlock(block)
        more=True
        offset=0
        directories={}
        try:
            while more:
                inode:int=int.from_bytes(BlockData[0x0+offset:0x4+offset], "little")
                rec_len:int=int.from_bytes(BlockData[0x4+offset:0x6+offset], "little")
                namelength:int=BlockData[0x6+offset]
                filetype:int=BlockData[0x7+offset]
                name:str=BlockData[0x8+offset:0x8+offset+namelength].decode(encoding="utf-8")
                directories[name]=[True,BlockData[0x0+offset:0x8+offset+namelength]]
                offset+=rec_len

                if rec_len==0:
                    more=False
                    break

                if offset>=len(BlockData):
                    more=False
                    break
        except UnicodeDecodeError as e:
            print("Got a UnicodeDecodeError, not a directory.")
            if ThrowErrorsBack:
                raise UnicodeDecodeError(e)
            else:
                return {}
            
        return directories

    def readFileInodeBytes(self, inode_num: int) -> bytes:
        inode = self.GetInode(inode_num)

        exTable=inode[0x28:0x28+60]
        entries=self.ParseExtentTree(exTable)
        
        mode = int.from_bytes(inode[0x00:0x02], "little") & 0xF000 #remove them perms
        if mode != 0x8000:
            print(f"not a regular file: {hex(mode)}")
            return
        
        i_size_lo = int.from_bytes(inode[0x04:0x08], "little")
        i_size_hi = int.from_bytes(inode[0x6C:0x70], "little")
        file_size = (i_size_hi << 32) | i_size_lo
        data:bytes=b''
        for Block, length in entries:
            for i in range(0,length):
                
                data += self.GetBlock(Block + i)
        
        return data[0:file_size]

        

        




    #feel free to make this better
    def readPath(self, AbsolutePath:str)->tuple[list, int]:
        if not AbsolutePath.startswith("/"):
            print("Not an absolute path")
            return
        
        paths=AbsolutePath.split("/")[1:]
        finalPathEntries=[]
        filetype=0
        dirBlock={}
        inode = self.GetInode(2)
        Entries=self.ParseExtentTree(inode[0x28:0x28+60])
        for blockNum, __ in Entries:
            dirBlock=self._ParseBlockDirectories_(blockNum)

        if AbsolutePath.replace(" ","")=="/":
            return dirBlock, 2

        for entry in paths:
            if entry.replace(" ","") == '':
                continue
            if not entry in dirBlock:
                return {"error":"notadir"}
            filetype=dirBlock[entry][4]
            if filetype==1:
                dirBlock={"File":dirBlock[entry][5]}
            else:
                inode = self.GetInode(dirBlock[entry][1])
                Entries=self.ParseExtentTree(inode[0x28:0x28+60])
                for blockNum, __ in Entries:
                    dirBlock=self._ParseBlockDirectories_(blockNum)
        
        finalPathEntries=dirBlock
        return finalPathEntries, filetype

    def readFile(self, AbsolutePath:str)->tuple[bytes, int]:
        if not AbsolutePath.startswith("/"):
            print("Not an absolute path")
            return
        
        
        fileBytes=b''
        paths=AbsolutePath.split("/")[1:]
        filetype=0
        dirBlock={}
        inode = self.GetInode(2)
        Entries=self.ParseExtentTree(inode[0x28:0x28+60])
        for blockNum, __ in Entries:
            dirBlock=self._ParseBlockDirectories_(blockNum)

        if AbsolutePath.replace(" ","")=="/":
            return dirBlock, 0

        for entry in paths:
            if entry.replace(" ","") == '':
                continue
            if not entry in dirBlock:
                return {"error":"notadir"}
            tempfiletype=dirBlock[entry][4]
            if not tempfiletype==1:
                inode = self.GetInode(dirBlock[entry][1])
                Entries=self.ParseExtentTree(inode[0x28:0x28+60])
                for blockNum, __ in Entries:
                    dirBlock=self._ParseBlockDirectories_(blockNum)
            else:
                fileBytes=self.readFileInodeBytes(dirBlock[entry][1])
                filetype=1

        
        return fileBytes, filetype

            

    def rewrite(self, path:str, file:str, data:bytes):... #adding this when I gain more knowledge on EXT4 filesystems, it looks really hard, maybe im wrong but idk.