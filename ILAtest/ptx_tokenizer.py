import re
import pickle
import sys

test_file_name = 'backprop_cuda_kernel1.ptx'
test_file_name = sys.argv[1]
#'backprop_cuda_kernel2.ptx'
#'bfs_kernel.ptx'
test_file_obj = open(test_file_name, 'r')
test_file_code = test_file_obj.readlines()
instruction_book_file = 'instruction_book'
instruction_book_obj = open(instruction_book_file, 'r')
instruction_book = instruction_book_obj.readlines()
for i in range(len(instruction_book)):
    instruction_book[i] = instruction_book[i][:-1]
start_flag = '//start\n'

#Seperate declaration and imperative statements.
start_line = 0
for i in range(len(test_file_code)):
    raw_code = test_file_code[i]
    raw_code_token = raw_code.split()
    if len(raw_code_token) == 0:
        continue
    instruction_tokens = raw_code_token[0].split('.')
    if len(instruction_tokens) == 0:
        continue
    instruction = instruction_tokens[0]
    if instruction in instruction_book:
        start_line=i
        break

unchanged_code = test_file_code[:start_line]
process_code = test_file_code[start_line:]


shared_read_only_regs = []
local_regs = []
type_map = {}
type_map['%tid.x'] = '.b32'
type_map['%tid.y'] = '.b32'
type_map['%tid.z'] = '.b32'
type_map['%ctaid.x'] = '.b32'
type_map['%ctaid.y'] = '.b32'
type_map['%ctaid.z'] = '.b32'
type_map['%nctaid.x'] = '.b32'
type_map['%nctaid.y'] = '.b32'
type_map['%nctaid.z'] = '.b32'
type_map['%ntid.x'] = '.b32'
type_map['%ntid.y'] = '.b32'
type_map['%ntid.z'] = '.b32'
reg_pattern = re.compile(r'([_a-zA-Z\%\$]+)\<([0-9]+)\>',)
for i in range(len(unchanged_code)):
    a = re.split('\s|,|:|;', unchanged_code[i])
    a = filter(lambda a: a!='', a)
    unchanged_code[i] = a
    if len(a) >= 3:
        if a[0] == '.reg':
            match_reg = reg_pattern.match(a[2])
            if match_reg == None:
                type_map[a[2]] = a[1]
            else:
                name = match_reg.group(1)
                num = int(match_reg.group(2))
                for i in range(num):
                    type_map[name + str(i)] = a[1]
        if a[0] == '.param':
            if a[1] == '.align':
                param_pattern = re.compile(r'([_0-9a-zA-Z\%\$]+)\[([0-9]+)\]')
                match_pointer = param_pattern.match(a[4])
                if match_pointer == None:
                #Just for this case
                    type_map[a[4]] = '.b32'
                else:
                    name = match_pointer.group(1)
                    num = int(match_pointer.group(2))
                    #just for this case
                    type_map[name] = '.b32'
           # type_map[shared_memory_address] = (alignment, size-unit, total units)
 
            else:
                type_map[a[2]] = a[1]

        if (a[0] == ".shared") | (a[0] == ".global") | (a[0] == '.const'):  #come from Nvidia matrix multiply example.
            if a[1] == '.texref':#Some unused suffix
                continue
            if len(a) < 5:
                if a[1] == '.surfref':
                    type_map[a[2] + '0'] = '.b32'
                    type_map[a[2] + '1'] = '.b32'
                    type_map[a[2] + '2'] = '.b32'
                    shared_read_only_regs.append(a[2] + '0')
                    shared_read_only_regs.append(a[2] + '0')
                    shared_read_only_regs.append(a[2] + '0')
                else:
                    type_map[a[2]] = '.b32'
                continue
            shared_pattern = re.compile(r'([_0-9a-zA-Z\%\$]+)\[([0-9]*)\]')
            match_pointer = shared_pattern.match(a[4])
            if match_pointer == None:
                type_map[a[4]] = (a[2], a[3])
                #Just for this case
                type_map[a[4]] = '.b32'
                shared_read_only_regs.append(a[4])
            else:
                name = match_pointer.group(1)
                #num = int(match_pointer.group(2))
                shared_read_only_regs.append(name)
                #for i in range(num):
                #    type_map[name] = (a[2], a[3], match_pointer.group(2))
                #just for this case
                type_map[name] = '.b32'
           # type_map[shared_memory_address] = (alignment, size-unit, total units)
        if a[0] == ".local":
            local_pattern = re.compile(r'([_0-9a-zA-Z\%\$]+)\[([0-9]+)\]')
            match_pointer = local_pattern.match(a[4])
            if match_pointer == None:
                type_map[a[4]] = (a[2], a[3])
                #Just for this case.
                type_map[a[4]] = '.b32'
                local_regs.append(a[4])
            else:
                name = match_pointer.group(1)
                num = int(match_pointer.group(2))
                local_regs.append(name)
                for i in range(num):
                    type_map[name] = (a[2], a[3], match_pointer.group(2))
                type_map[name] = '.b32'

process_code_split = []
for i in range(len(process_code)):
    a = re.split('\s|,|;', process_code[i])
    a = filter(lambda a: a != '', a)
    process_code[i] = a
ssa_counter = 0
reg_map = {}
parenthesis = []
parenthesis_re = re.compile(r'\[[a-zA-Z0-9\%\_\+\$\-]+\]')
for i in range(len(process_code)):
    for j in range(len(process_code[i])):
        if parenthesis_re.match(process_code[i][j]) != None:
            parenthesis.append((i, j))
            process_code[i][j] = process_code[i][j][1:-1]

#Remove ld.param
for i in range(len(process_code)):
    process_code_line = process_code[i]
    if len(process_code_line) < 1:
        continue
    opcode = process_code_line[0]
    opcode_split = re.split('\.', opcode)
    if (opcode_split[0] == 'ld'):
        if (opcode_split[1] == 'param'):
            if(opcode_split[2][-2:] == '64'):
                process_code[i] = []
                shared_read_only_regs.append(process_code_line[1])
#print process_code
shared_read_only_obj = open('shared_read_only_regs', 'w')
pickle.dump(shared_read_only_regs, shared_read_only_obj)
shared_read_only_obj.close()
local_regs_obj = open('local_regs', 'w')
pickle.dump(local_regs, local_regs_obj)
local_regs_obj.close()

code_line_num = 0
for i in range(len(process_code)):
    process_code_line = process_code[i]
    if len(process_code_line) < 1:
        continue
    if len(process_code_line) > 1:
        code_line_num += 1
    opcode = process_code_line[0]
    if opcode[0] == '@':
        branch = opcode
        predicate_reg = branch[1:]
        process_code_line = [branch[0], predicate_reg] + process_code_line[1:]
        process_code[i] = process_code_line
        continue
#print code_line_num
#for process_code_line in process_code:
#    print process_code_line
'''
for i in range(len(process_code)):
    for j in range(len(process_code[i])):
        if (i, j) in parenthesis:
            process_code[i][j] = '[' + process_code[i][j] + ']' 

print_code = []
for i in range(len(process_code)):
    process_line = process_code[i]
    if len(process_line) == 0:
        print_line = '\n'
        print_code.append(print_line)
        continue
    if len(process_line) == 1:
        if process_line[0] in instruction_book:
            print_line = process_line[0] + ';' + '\n'
            print_code.append(print_line)
        else:
            print_code.append(process_line[0] + '\n')
        continue
    print_line = '    '
    print_flag = True
    for process_token in process_line:
        print_line += process_token
        if print_flag:
            print_line += '    '
            print_flag = False
        else:
            print_line += ' ,'
    print_line = print_line[:-2]
    print_line += ';\n'
    print_code.append(print_line)
ssa_print_code_obj = open('ssa_print_code.ptx', 'w')
ssa_print_code_obj.writelines(print_code)
ssa_print_code_obj.close()
'''
declaration_file = 'ptx_declaration_file'
declaration_obj = open(declaration_file, 'w')
pickle.dump(type_map, declaration_obj)
declaration_obj.close()
#print type_map

#ssa_file = 'ptx_add_neighbor'
#ssa_obj = open(ssa_file, 'w')
##ssa_obj.writelines(print_code)
#pickle.dump(process_code, ssa_obj)
#ssa_obj.close()
##print process_code


######################################Extra Pass To Delete Dead Code#################
addr_dest = []
i = 0
for process_code_line in process_code:
    if len(process_code_line) > 1:
        if (process_code_line[0].find('f32') != -1):
            i += 1
        inst = process_code_line[0]
        #find all ld addresses
        if inst[:2] == 'ld':
            if inst.find('acq') != -1:
                addr = process_code_line[1]
            else:
                addr = process_code_line[2]
            if addr.find('+') != -1:
                addr = addr[:addr.find('+')]
            if addr not in addr_dest:
                if addr[0] == '%':
                    addr_dest.append(addr)
        #find all st
        if inst[:2] == 'st':
            addr = process_code_line[1]
            #print addr
            if addr.find('+') != -1:
                addr = addr[:addr.find('+')]
            if addr not in addr_dest:
                if addr[0] == '%':
                    addr_dest.append(addr)
        if inst == '@':
            pred = process_code_line[1]
            if pred[0] == '!':
                pred = pred[1:]
            if pred not in addr_dest:
                if pred[0] == '%':
                    addr_dest.append(pred) 
        if inst[:4] == 'atom':
            addr = process_code_line[2]
            if addr.find('+') != -1:
                addr = addr[:addr.find('+')]
            if addr not in addr_dest:
                if addr[0] == '%':
                    addr_dest.append(addr)
#print i

#print addr_dest
while(True):
    flag = True
    for process_code_line in process_code:
        if len(process_code_line) > 1:
            inst = process_code_line[0]
            if inst == '@':
                continue
            if inst.find('bra') != -1:
                continue
            if inst.find('bar') != -1:
                continue
            if inst[:2] == 'ld':
                continue
            if inst[:2] == 'st':
                continue
            if inst[:4] == 'atom':
                continue
            dest_op = process_code_line[1]
            if dest_op not in addr_dest:
                continue
            for op in process_code_line[2:]:
                if op not in addr_dest:
                    flag = False
                    addr_dest.append(op)
            
    if flag:
        break
#print addr_dest
new_process_code = []
line_num = 0
for process_code_line in process_code:
    if len(process_code_line) < 1:
        continue
    #print process_code_line
    line_num += 1
    if len(process_code_line) == 1:
        if process_code_line[0] == '}':
            continue
        if process_code_line[0] == 'ret':
            continue
        new_process_code.append(process_code_line)
        continue
    inst = process_code_line[0]
    if inst == '@':
        new_process_code.append(process_code_line)
        continue
    if inst.find('bra') != -1:
        new_process_code.append(process_code_line)
        continue
    if inst.find('bar') != -1:
        new_process_code.append(process_code_line)
        continue
    if inst[:2] == 'ld':
        new_process_code.append(process_code_line)
        continue
    if inst[:2] == 'st':
        new_process_code.append(process_code_line)
        continue
    if inst[:4] == 'atom':
        new_process_code.append(process_code_line)
        continue
    dest_opcde = process_code_line[1]
    if dest_opcde in addr_dest:
        if inst[-3] == 'f':
            if inst.find('setp') == -1:
                #print process_code_line
                continue
        new_process_code.append(process_code_line)
#print len(process_code)
print len(new_process_code)
print line_num
ssa_file = 'ptx_add_neighbor'
ssa_obj = open(ssa_file, 'w')
#ssa_obj.writelines(print_code)
pickle.dump(new_process_code, ssa_obj)
ssa_obj.close()
#for p in new_process_code:
    #print(p)
print('#########################################')
zero_starter = []
for process_code_line in new_process_code:
    inst = process_code_line[0]
    if inst == '@':
        continue
    if inst.find('bra') != -1:
        continue
    if inst.find('bar') != -1:
        continue
    if inst[:2] == 'ld':
        continue
    if inst[:2] == 'st':
        continue
    if len(process_code_line) == 1:
        continue
    if (process_code_line[1][1] == 'p'):
        continue
    #print(process_code_line)
    zero_starter.append(process_code_line[1])
zero_starter_obj = open('zero_starter', 'w')  
pickle.dump(zero_starter, zero_starter_obj)
zero_starter_obj.close()              

#print zero_starter
            
            
     

                

        
