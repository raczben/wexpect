import os
import glob

read_files = glob.glob(".wlog/*.log")

for f in read_files:
    with open(f, "r") as infile:
        print(infile.read())
        

read_files = glob.glob("tests/.wlog/*.log")

for f in read_files:
    with open(f, "rb") as infile:
        print(infile.read())