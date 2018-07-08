import re
import pickle
import sys
SRC_FILE = "files/"
REG_TYPE = '.b32'
PARAM_MEM_TYPE = '.b32'
SHARED_MEM_TYPE = '.b32'
LOCAL_MEM_TYPE = 'b32'
MULTI_REG_RE_EXP = r'([_a-zA-Z\%\$]+)\<([0-9]+)\>'
REG_SPLIT_RE_EXP = '\s|,|:|;'
MULTI_PARAM_RE_EXP = r'([_0-9a-zA-Z\%\$]+)\[([0-9]+)\]'
MULTI_SHARED_RE_EXP = r'([_0-9a-zA-Z\%\$]+)\[([0-9]*)\]'
MULTI_LOCAL_RE_EXP = r'([_0-9a-zA-Z\%\$]+)\[([0-9]+)\]'
CODE_SPLIT_RE_EXP = '\s|,|;'
PARENTHESIS_RE_EXP = r'\[[a-zA-Z0-9\%\_\+\$\-]+\]'
REG = '.reg'
PARAM = '.param'
ALIGN = '.align'
SHARED = '.shared'
CONST = '.const'
GLOBAL = '.global'
LOCAL = '.local'
TEX = '.texref'
SUR = '.surfref'
EFF_REG_LENGTH = 3
USELESS_CODE_LENGTH = 1
EFF_MEM_LENGTH = 5
LD_INST = 'ld'
LD_ACQ_INST = 'acq'
ST_INST = 'st'
ST_REL_INST = 'rel'
ATOM_INST = 'atom'
LD_PARAM_A = 'ld'
LD_PARAM_B = 'param'
LD_PARAM_C = '64'
SHARED_RO_REGFILE = 'shared_read_only_regs'
LOCAL_REGFILE = 'local_regs'

test_file_name = 'backprop_cuda_kernel1.ptx'
test_file_name = SRC_FILE + sys.argv[1]
#'backprop_cuda_kernel2.ptx'
#'bfs_kernel.ptx'
test_file_obj = open(test_file_name, 'r')
test_file_code = test_file_obj.readlines()
instruction_book_file = SRC_FILE + 'instruction_book'
instruction_book_obj = open(instruction_book_file, 'r')
instruction_book = instruction_book_obj.readlines()
for i in range(len(instruction_book)):
    instruction_book[i] = instruction_book[i][:-1]
start_flag = '//start\n'
##########################################################################################
######### Seperate declaration and imperative statements #################################
##########################################################################################
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
declarative_code = test_file_code[:start_line]
process_code = test_file_code[start_line:]

##########################################################################################
############## Extract states from declarative statements ################################
##########################################################################################
shared_read_only_regs = []
local_regs = []
type_map = {}
type_map['%tid.x'] = REG_TYPE
type_map['%tid.y'] = REG_TYPE
type_map['%tid.z'] = REG_TYPE
type_map['%ctaid.x'] = REG_TYPE
type_map['%ctaid.y'] = REG_TYPE
type_map['%ctaid.z'] = REG_TYPE
type_map['%nctaid.x'] = REG_TYPE
type_map['%nctaid.y'] = REG_TYPE
type_map['%nctaid.z'] = REG_TYPE
type_map['%ntid.x'] = REG_TYPE
type_map['%ntid.y'] = REG_TYPE
type_map['%ntid.z'] = REG_TYPE
multi_reg_pattern = re.compile(MULTI_REG_RE_EXP,)
for i in range(len(declarative_code)):
    a = re.split(REG_SPLIT_RE_EXP, declarative_code[i])
    a = filter(lambda a: a!='', a)
    declarative_code[i] = a
    if len(a) < EFF_REG_LENGTH:
        continue
    else:
        if a[0] == REG:
            reg_dec = a
            match_reg = multi_reg_pattern.match(reg_dec[2])
            if match_reg == None:
                type_map[reg_dec[2]] = reg_dec[1]
            else:
                multi_reg_name = match_reg.group(1)
                num = int(match_reg.group(2))
                for i in range(num):
                    type_map[multi_reg_name + str(i)] = reg_dec[1]
        if a[0] == PARAM:
            param_dec = a
            if param_dec[1] == ALIGN:
                multi_param_pattern = re.compile(MULTI_PARAM_RE_EXP)
                match_pointer = multi_param_pattern.match(param_dec[4])
                if match_pointer == None:
                #Just for this case
                    type_map[param_dec[4]] = PARAM_MEM_TYPE
                else:
                    multi_param_name = match_pointer.group(1)
                    num = int(match_pointer.group(2))
                    type_map[multi_param_name] = PARAM_MEM_TYPE
                    #just for this case
            else:
                type_map[param_dec[2]] = param_dec[1]

        if (a[0] == SHARED) | (a[0] == GLOBAL) | (a[0] == CONST):  #From Nvidia matrix multiply example.
            mem_dec = a
            if mem_dec[1] == TEX:#Read Only Suffix
                continue
            if len(mem_dec) < EFF_MEM_LENGTH:
                if mem_dec[1] == SUR:
                    #Three Dimensions
                    type_map[mem_dec[2] + '0'] = PARAM_MEM_TYPE
                    type_map[mem_dec[2] + '1'] = PARAM_MEM_TYPE
                    type_map[mem_dec[2] + '2'] = PARAM_MEM_TYPE
                    shared_read_only_regs.append(mem_dec[2] + '0')
                    shared_read_only_regs.append(mem_dec[2] + '0')
                    shared_read_only_regs.append(mem_dec[2] + '0')
                else:
                    type_map[mem_dec[2]] = REG_TYPE
                continue
            else:
                multi_shared_pattern = re.compile(MULTI_SHARED_RE_EXP)
                match_pointer = multi_shared_pattern.match(mem_dec[4])
                if match_pointer == None:
                    #Just for this case
                    type_map[mem_dec[4]] = SHARED_MEM_TYPE
                    shared_read_only_regs.append(mem_dec[4])
                else:
                    multi_shared_name = match_pointer.group(1)
                    #num = int(match_pointer.group(2))
                    shared_read_only_regs.append(multi_shared_name)
                    type_map[multi_shared_name] = SHARED_MEM_TYPE
        if a[0] == LOCAL:
            local_dec = a
            multi_local_pattern = re.compile(MULTI_LOCAL_RE_EXP)
            match_pointer = multi_local_pattern.match(local_dec[4])
            if match_pointer == None:
                #Just for this case.
                type_map[local_dec[4]] = LOCAL_MEM_TYPE
                local_regs.append(local_dec[4])
            else:
                multi_local_name = match_pointer.group(1)
                num = int(match_pointer.group(2))
                local_regs.append(multi_local_name)
                type_map[multi_local_name] = LOCAL_MEM_TYPE

##########################################################################################
############## Split opcode&operands, clear parenthesis ##################################
##########################################################################################

process_code_split = []
for i in range(len(process_code)):
    a = re.split(CODE_SPLIT_RE_EXP, process_code[i])
    a = filter(lambda a: a != '', a)
    process_code[i] = a

reg_map = {}
parenthesis_re = re.compile(PARENTHESIS_RE_EXP)
for i in range(len(process_code)):
    for j in range(len(process_code[i])):
        if parenthesis_re.match(process_code[i][j]) != None:
            process_code[i][j] = process_code[i][j][1:-1]



##########################################################################################
############## Remove ld.param ###########################################################
##########################################################################################

for i in range(len(process_code)):
    process_code_line = process_code[i]
    if len(process_code_line) < 1:
        continue
    opcode = process_code_line[0]
    opcode_split = re.split('\.', opcode)
    if (opcode_split[0] == LD_PARAM_A):
        if (opcode_split[1] == LD_PARAM_B):
            if(opcode_split[2][-2:] == LD_PARAM_C):
                process_code[i] = []
                shared_read_only_regs.append(process_code_line[1])


##########################################################################################
############## Store Parameter Regs       ################################################
############## Store General&Special Regs ################################################
##########################################################################################



shared_read_only_obj = open(SHARED_RO_REGFILE, 'w')
pickle.dump(shared_read_only_regs, shared_read_only_obj)
shared_read_only_obj.close()
local_regs_obj = open(LOCAL_REGFILE, 'w')
pickle.dump(local_regs, local_regs_obj)
local_regs_obj.close()

declaration_file = 'ptx_declaration_file'
declaration_obj = open(declaration_file, 'w')
pickle.dump(type_map, declaration_obj)
declaration_obj.close()


##########################################################################################
############## Lexer                           ###########################################
############## TODO: This is an extremely easy ###########################################
##############       lexer, need improvement   ###########################################
##############       for other use.            ###########################################
##########################################################################################

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


##########################################################################################
############# Extra Pass To Dead Code ####################################################
##########################################################################################


addr_dest = []
for process_code_line in process_code:
    if len(process_code_line) > USELESS_CODE_LENGTH:
        opcode = process_code_line[0]
        #find all ld addresses
        if opcode[:2] == LD_INST:
            if opcode.find(LD_ACQ_INST) != -1:
                addr = process_code_line[1]
            else:
                addr = process_code_line[2]
            if addr.find('+') != -1:
                addr = addr[:addr.find('+')]
            if addr not in addr_dest:
                if addr[0] == '%':
                    addr_dest.append(addr)
        #find all st
        if opcode[:2] == ST_INST:
            addr = process_code_line[1]
            #print addr
            if addr.find('+') != -1:
                addr = addr[:addr.find('+')]
            if addr not in addr_dest:
                if addr[0] == '%':
                    addr_dest.append(addr)
        if opcode == '@':
            pred = process_code_line[1]
            if pred[0] == '!':
                pred = pred[1:]
            if pred not in addr_dest:
                if pred[0] == '%':
                    addr_dest.append(pred) 
        if opcode[:4] == ATOM_INST:
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
            opcode = process_code_line[0]
            if opcode == '@':
                continue
            if opcode.find('bra') != -1:
                continue
            if opcode.find('bar') != -1:
                continue
            if opcode[:2] == 'ld':
                continue
            if opcode[:2] == 'st':
                continue
            if opcode[:4] == 'atom':
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
    opcode = process_code_line[0]
    if opcode == '@':
        new_process_code.append(process_code_line)
        continue
    if opcode.find('bra') != -1:
        new_process_code.append(process_code_line)
        continue
    if opcode.find('bar') != -1:
        new_process_code.append(process_code_line)
        continue
    if opcode[:2] == 'ld':
        new_process_code.append(process_code_line)
        continue
    if opcode[:2] == 'st':
        new_process_code.append(process_code_line)
        continue
    if opcode[:4] == 'atom':
        new_process_code.append(process_code_line)
        continue
    dest_opcde = process_code_line[1]
    if dest_opcde in addr_dest:
        if opcode[-3] == 'f':
            if opcode.find('setp') == -1:
                #print process_code_line
                continue
        new_process_code.append(process_code_line)
#print len(process_code)
print len(new_process_code)
print line_num
#for p in new_process_code:
    #print(p)
print('#########################################')
zero_starter = []
for process_code_line in new_process_code:
    opcode = process_code_line[0]
    if opcode == '@':
        continue
    if opcode.find('bra') != -1:
        continue
    if opcode.find('bar') != -1:
        continue
    if opcode[:2] == 'ld':
        continue
    if opcode[:2] == 'st':
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
            
            
     

                

        
