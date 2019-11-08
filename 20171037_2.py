import sys
import os
from copy import deepcopy

############# globals ############# 
database = dict()
database_ordered = list()
command = sys.argv
filename = command[1]
out_file = '20171037_2.txt'
###################################

if(len(command) != 2):
    sys.exit("Usage: python2 20171037_2.py input_file")

class UndoRecovery():

    def __init__(self,filename):
        self.filename = filename
        self.output = ""
        self.end_ckpt = False
        self.start_ckpt = False
        self.done_trans = list()

    def readfile(self):
        global database_ordered, database
        with open(self.filename, 'rb') as f:
            data_line = f.readlines()
        input_data = data_line
        data_line = input_data[0].strip().split()

        for i in range(0,len(data_line),2):
            cur = data_line[i]
            database_ordered.append(cur)
            database[cur] = int(data_line[i+1])

        input_data = input_data[1:]
        return input_data


    def recovery(self,input_data):
        global database, database_ordered
        self.done_trans = []
        cnt=0
        self.end_ckpt = False
        self.start_ckpt = False
        inconsistent = []
        for entry in reversed(input_data):
            entry = entry.strip()
            if entry == "<END CKPT>":
                self.end_ckpt = True
                    
            elif "START" in entry:
                if self.start_ckpt:
                    _, tr = entry[1:-1].split()
                    tr = tr.strip()
                    if tr in inconsistent and cnt + 1 == len(inconsistent):
                        cnt += 1
                        break

            elif entry == '':
                continue

            elif "COMMIT" in entry:
                entry = entry[:0] + entry[1:]
                self.done_trans.append((entry[1:-1].split()[1]).strip())

            elif "START CKPT" in entry:
                if self.end_ckpt:
                    break

                inconsistent = []
                line1 = deepcopy(entry)
                line1 = line1[:0] + line1[1:]
                line1 = ((line1.strip()).split()[2]).strip()
                if '(' == line1[0]:
                    line1 = line1[:0] + line1[1:]
                for tr in line1.split(','):
                    tr = tr.strip()
                    if tr in self.done_trans:
                        continue
                    inconsistent.append(tr)

                self.start_ckpt = True
                cnt=0
            elif len(entry.split(',')) == 3:
                id = entry.rfind(',')
                line1 = entry[:id]
                value = entry[id+1:-1]
                line1 = line1[1:]
                tr, element = line1.split(',')
                tr = tr.strip()
                element =  element.strip()
                value = int(value.strip())
                if tr not in self.done_trans:
                    database[element] = value


recover = UndoRecovery(filename)
input_data = recover.readfile()
database_ordered.sort()
recover.recovery(input_data)

recover.end_ckpt = False
recover.start_ckpt = False
inconsistent = []

for entry in reversed(input_data):
    entry = entry.strip()
    if entry == "" :
        continue
    elif entry == "<END CKPT>":
        recover.end_ckpt = True
            
    elif "COMMIT" in entry:
        entry = entry[:0] + entry[1:]
        _, tr = entry.split()
        recover.done_trans.append(tr.strip())

    elif "START" in entry:
        if recover.start_ckpt:
            if cnt + 1 == len(inconsistent):
                break

    elif "START CKPT" in entry:
        line1 = deepcopy(entry)
        inconsistent = []
        line1 = line1[:0] + line1[1:]
        line1 = ((line1.strip()).split()[2]).strip()
        if recover.end_ckpt:
            break

        if '(' == line1[0]:
            line1 = line1[:0] + line1[1:]
        for tr in line1.split(','):
            tr = tr.strip()
            if tr in recover.done_trans:
                continue
            inconsistent.append(tr)

        recover.start_ckpt = True
        cnt=0

    elif entry.count(',') == 2:
        id = entry.rfind(',')
        line1 = entry[:id]
        value = entry[id+1:-1]
        line1 = line1[1:]
        tr, element = line1.split(',')
        tr = tr.strip()
        element =  element.strip()
        value = int(value.strip())
        if tr not in recover.done_trans:
            database[element] = value


for idx, element in enumerate(database_ordered):
    recover.output += str(element) 
    recover.output += " " 
    recover.output += str(database[element])
    if idx != len(database_ordered) - 1 : 
        recover.output = recover.output + ' '
recover.output+='\n'

with open(out_file, 'w+') as out_file:
    out_file.write(recover.output)

