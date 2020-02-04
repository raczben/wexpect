import os
import glob

read_files = []

read_files += glob.glob("*.log")
read_files += glob.glob(".wlog/*.log")
read_files += glob.glob("tests/.wlog/*.log")

read_files.sort(key=lambda x: os.path.getmtime(x))

for f in read_files:
    print()
    print(f)
    print()
    with open(f, "r") as infile:
        print(infile.read())