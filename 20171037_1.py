import sys
import os


########### GLOBALS ###########
transactions = {}
database = {}
memory = {}
registers = {}
memory_ordered = []
ord_tmp = []
database_ordered = []
command = sys.argv
x = command[-1]
filename = command[1]
###############################

if len(command)!=3:
    sys.exit("Usage: python 20171037_1.py input_file x")


class UndoLog():

    def __init__(self):
        self.output = ""
        self.start = True

    def order_render(self):
        global memory_ordered, memory

        memory_ordered.sort()
        for idx, element in enumerate(memory_ordered):
            self.output = self.output + str(element)
            self.output = self.output + " "
            self.output = self.output + str(memory[element])
            if idx + 1 !=len(memory_ordered):
                self.output += ' '

        self.output += '\n'

        global database_ordered, database
        for idx, element in enumerate(database_ordered):
            self.output = self.output + str(element)
            self.output = self.output + " "
            self.output = self.output + str(database[element])

            if idx + 1 != len(database_ordered):
                self.output = self.output + ' '
        self.output += '\n'

    def database_query(self,command, operation, tr_id):
        global database, registers, memory, memory_ordered
        command = ((command.split('(')[1]).split(')')[0]).strip()

        if(',' in command):
            element, register = command.split(',')
            element = element.strip()
            register = register.strip()

        if(operation == "output"):
            if(command in memory):
                database[command] = memory[command]
            else:
                memory_ordered.append(command)
                memory[command] = database[command]
        elif(operation == "read"):
            if element in memory:
                registers[register] = memory[element]
            else:
                registers[register] = database[element]
                memory[element] = database[element]
                memory_ordered.append(element)
        elif(operation == "write"):
            self.output = self.output + "<" 
            self.output = self.output + tr_id 
            self.output = self.output + ", "
            self.output = self.output + element 
            self.output = self.output + ", "
            if element in memory:
                pass
            else:
                memory[element] = database[element]
                memory_ordered.append(element)
            tmp = str(memory[element]) + ">" + '\n'
            self.output = self.output + str(memory[element])
            self.output = self.output + ">" 
            self.output = self.output + "\n"
            memory[element] = registers[register]
            self.order_render()
        
    def execute(self,tr_id, start_comm, end_comm):
        operators = ['+', '-', '*', '/']

        operations = ["output", "read", "write"]
        global transactions, registers
        for idx in range(start_comm, end_comm):
            comm = transactions[tr_id]
            fl = False
            comm = comm[idx]
            for operation in operations:
                if operation in comm.lower():
                    fl = True
                    break
                else:
                    pass

            if fl: 
                self.database_query(comm, operation, tr_id)
                continue

            command = comm
            command = command.strip()
            command = command.split(":=")
            final_reg = command[0].strip()
            for operation in operators:
                if operation in command[1]:

                    if(operation == '/'):
                        input1, inp2 = command[1].strip().split(operation)
                        input1 = input1.strip()
                        inp2 = inp2.strip()

                        try: input1 = int(input1)
                        except: input1 = registers[input1]

                        try: inp2 = int(inp2)
                        except: inp2 = registers[inp2]
                        registers[final_reg] = input1
                        if(inp2 != 0):
                            registers[final_reg] = registers[final_reg] / inp2
                        else:
                            print("Divide by zero")
                            sys.exit(-1)
                    elif operation == '-':
                        input1, inp2 = command[1].strip().split(operation)
                        input1 = input1.strip()
                        inp2 = inp2.strip()

                        try: input1 = int(input1)
                        except: input1 = registers[input1]

                        try: inp2 = int(inp2)
                        except: inp2 = registers[inp2]
                        registers[final_reg] = input1
                        registers[final_reg] = registers[final_reg] - inp2
                    elif(operation == '+'):
                        input1, inp2 = command[1].strip().split(operation)
                        input1 = input1.strip()
                        inp2 = inp2.strip()

                        try: input1 = int(input1)
                        except: input1 = registers[input1]

                        try: inp2 = int(inp2)
                        except: inp2 = registers[inp2]
                        registers[final_reg] = input1
                        registers[final_reg] = registers[final_reg] + inp2
                    elif operation == '*':
                        input1, inp2 = command[1].strip().split(operation)
                        input1 = input1.strip()
                        inp2 = inp2.strip()

                        try: input1 = int(input1)
                        except: input1 = registers[input1]

                        try: inp2 = int(inp2)
                        except: inp2 = registers[inp2]
                        registers[final_reg] = input1

                        registers[final_reg] = registers[final_reg] * inp2
                    break

    def operate(self,num_ops):
        start_point = 0
        completed = False
        num_ops = int(num_ops)
        global transactions, ord_tmp
        while 1:
            start_comm = start_point * num_ops
            cnt = 0
            fl1 = False
            for tr in ord_tmp:
                
                transtr = transactions[tr]
                tr_num_cmd = len(transtr)
                end_comm =  min(start_comm + num_ops, tr_num_cmd)
                if start_comm == 0 :
                    tmp = "<START "
                    tmp += tr 
                    tmp += ">" 
                    tmp += '\n'
                    self.output = self.output + tmp
                    self.order_render()
                self.execute(tr, start_comm, end_comm)
                if end_comm == tr_num_cmd:
                    self.output += "<COMMIT"
                    self.output += " " 
                    self.output += tr
                    self.output += ">"
                    self.output += '\n'
                    self.order_render()
                
                if start_comm >= tr_num_cmd:
                    cnt += 1
                    continue

            start_point += 1
            if cnt == len(ord_tmp):
                fl1 = True

            if fl1:
                break

    def read_input(self,filename):
        global transactions, database, database_ordered
        num_commands = 0
        self.start = True
        
        with open(filename, 'r') as f:
            for line in f:
                if self.start:
                    line = line.strip().split()
                    self.start = False
                    for i in range(0,len(line), 2):
                        cur = line[i]
                        database_ordered.append(cur)
                        cur2 = line[i+1]
                        database[cur] = int(cur2)

                elif line.strip() != '':
                    if num_commands:
                        transactions[tr_id].append(line.strip())
                        num_commands-=1
                    else:
                        tr_id, num_commands = line.strip().split()
                        tr_id, num_commands = tr_id.strip(), num_commands.strip()
                        num_commands = int(num_commands)
                        if tr_id in ord_tmp:
                            sys.exit("Transaction ID is repeated!")
                        else:
                            ord_tmp.append(tr_id)
                            transactions[tr_id] = []



undolog = UndoLog()


undolog.read_input(filename)
undolog.operate(x)
final_out = undolog.output

# output_file = "demoss_1.txt"
with open("20171037_1.txt", 'w+') as f:
    f.write(final_out)