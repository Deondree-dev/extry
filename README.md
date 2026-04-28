## Welcome to extry

Extry is a tool to view linux filesystems in windows, it was created but Deondree-dev but I would really love help with this as I cannot write the cleanest code.

## Contributing Rules:
Please dont use AI for fixing this tool, its ment to be a skill based project, not vibecoded
No viruses, malware, or any ware build into the tool.
Be patient.

## Running and using
So far only EXT4 filesystems are readable and if you have user eCrypt enabled you cant browse your home/<username> file system, along with some others.
when you download this tool, go into ./extry and run ```python main.py```, thats it.
It CLI only for now, but hopefully I or someone else can get a GUI working.
when your acatually in the filesystem there are only 3 commands.
ls (E.x: "ls /", "ls ", if you do "ls" nothing will happen)
cd (E.x: "cd var/log". is jsut the basic version of linux's cd, no argument)
cwd (prints your directory history, but if someone could fix it into making it be your actual current directly, that would be great)
cat (E.x: "cat /var/log/kern.log". Prints a file contents)
More coming soon.
I have plans to add other commands to copy files and write files, but Im scared at add writting.
