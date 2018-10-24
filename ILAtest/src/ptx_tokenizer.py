import re
import pickle
import sys


FILE_DIR = 'files/'
TMP_DIR = 'tmp/'
# (TODO: Yue Xing) Store these data into a separater file.
class STATE_TYPES:
    REG_TYPE = '.b32'
    PARAM_MEM_TYPE = '.b32'
    SHARED_MEM_TYPE = '.b32'
    LOCAL_MEM_TYPE = '.b32'


class STATE_RE_EXP:
    MULTI_REG_RE_EXP = r'([_a-zA-Z\%\$]+)\<([0-9]+)\>'
    REG_SPLIT_RE_EXP = '\s|,|:|;'
    MULTI_PARAM_RE_EXP = r'([_0-9a-zA-Z\%\$]+)\[([0-9]+)\]'
    MULTI_SHARED_RE_EXP = r'([_0-9a-zA-Z\%\$]+)\[([0-9]*)\]'
    MULTI_LOCAL_RE_EXP = r'([_0-9a-zA-Z\%\$]+)\[([0-9]+)\]'
    CODE_SPLIT_RE_EXP = '\s|,|;'
    PARENTHESIS_RE_EXP = r'\[[a-zA-Z0-9\%\_\+\$\-]+\]'


class PTX_DECL_TYPE:
    REG = '.reg'
    PARAM = '.param'
    ALIGN = '.align'
    SHARED = '.shared'
    CONST = '.const'
    GLOBAL = '.global'
    LOCAL = '.local'
    TEX = '.texref'
    SURF = '.surfref'


class PTX_MEM_INST:
    LD_INST = 'ld'
    LD_ACQ_INST = 'acq'
    ST_INST = 'st'
    ST_REL_INST = 'rel'
    ATOM_INST = 'atom'
    LD_PARAM_A = 'ld'
    LD_PARAM_B = 'param'
    LD_PARAM_C = '64'

         
class EFF_PARAMETER:
    EFF_REG_LENGTH = 3
    USELESS_CODE_LENGTH = 1
    EFF_MEM_LENGTH = 5


class DECL_FILE:
    SHARED_READONLY_REGFILE = 'shared_readonly_regs'
    LOCAL_REGFILE = 'local_regs'

if __name__ == "__main__":
    test_file_name = sys.argv[1]
    test_file_obj = open(test_file_name, 'r')
    test_file_code = test_file_obj.readlines()
    test_file_obj.close()
    instruction_book_file = FILE_DIR + 'instruction_book'
    instruction_book_obj = open(instruction_book_file, 'r')
    instruction_book = instruction_book_obj.readlines()
    for i in range(len(instruction_book)):
        instruction_book[i] = instruction_book[i][:-1]
    start_flag = '//start\n'
    ##########################################################################################
    ######### Seperate declaration and imperative statements #################################
    ##########################################################################################
    imperative_start_line = 0
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
            imperative_start_line=i
            break
    declarative_code = test_file_code[:imperative_start_line]
    process_code = test_file_code[imperative_start_line:]

    ##########################################################################################
    ############## Extract states from declarative statements ################################
    ##########################################################################################
    shared_read_only_regs = []

    local_regs = []
    type_map = {}
    type_map['%tid.x'] = STATE_TYPES.REG_TYPE
    type_map['%tid.y'] = STATE_TYPES.REG_TYPE
    type_map['%tid.z'] = STATE_TYPES.REG_TYPE
    type_map['%ctaid.x'] = STATE_TYPES.REG_TYPE
    type_map['%ctaid.y'] = STATE_TYPES.REG_TYPE
    type_map['%ctaid.z'] = STATE_TYPES.REG_TYPE
    type_map['%nctaid.x'] = STATE_TYPES.REG_TYPE
    type_map['%nctaid.y'] = STATE_TYPES.REG_TYPE
    type_map['%nctaid.z'] = STATE_TYPES.REG_TYPE
    type_map['%ntid.x'] = STATE_TYPES.REG_TYPE
    type_map['%ntid.y'] = STATE_TYPES.REG_TYPE
    type_map['%ntid.z'] = STATE_TYPES.REG_TYPE
    multi_reg_pattern = re.compile(STATE_RE_EXP.MULTI_REG_RE_EXP)
    for i in range(len(declarative_code)):
        a = re.split(STATE_RE_EXP.REG_SPLIT_RE_EXP, declarative_code[i])
        a = filter(lambda a: a!='', a)
        declarative_code[i] = a
        if len(a) < EFF_PARAMETER.EFF_REG_LENGTH:
            continue
        else:
            if a[0] == PTX_DECL_TYPE.REG:
                # (TODO: Yue Xing) the match structure is used multiple times. Refact it as a function.
                # Basically, we are trying to separater a and i from a[i]. 
                # If the input is a, then no need to do the separation.
                reg_dec = a
                match_reg = multi_reg_pattern.match(reg_dec[2])
                if match_reg == None:
                    type_map[reg_dec[2]] = reg_dec[1]
                else:
                    multi_reg_name = match_reg.group(1)
                    num = int(match_reg.group(2))
                    for i in range(num):
                        type_map[multi_reg_name + str(i)] = reg_dec[1]
            if a[0] == PTX_DECL_TYPE.PARAM:
                param_dec = a
                if param_dec[1] == PTX_DECL_TYPE.ALIGN:
                    multi_param_pattern = re.compile(STATE_RE_EXP.MULTI_PARAM_RE_EXP)
                    match_pointer = multi_param_pattern.match(param_dec[4])
                    if match_pointer == None:
                        type_map[param_dec[4]] = STATE_TYPES.PARAM_MEM_TYPE
                    else:
                        multi_param_name = match_pointer.group(1)
                        num = int(match_pointer.group(2))
                        type_map[multi_param_name] = STATE_TYPES.PARAM_MEM_TYPE
                else:
                    type_map[param_dec[2]] = param_dec[1]
    
            if (a[0] == PTX_DECL_TYPE.SHARED) | (a[0] == PTX_DECL_TYPE.GLOBAL) | (a[0] == PTX_DECL_TYPE.CONST):  #From Nvidia matrix multiply example.
                mem_dec = a
                if mem_dec[1] == PTX_DECL_TYPE.TEX:  #Read Only Suffix
                    continue
                if len(mem_dec) < EFF_PARAMETER.EFF_MEM_LENGTH:
                    if mem_dec[1] == PTX_DECL_TYPE.SURF:
                        #Surface has three dimensions
                        type_map[mem_dec[2] + '0'] = STATE_TYPES.PARAM_MEM_TYPE
                        type_map[mem_dec[2] + '1'] = STATE_TYPES.PARAM_MEM_TYPE
                        type_map[mem_dec[2] + '2'] = STATE_TYPES.PARAM_MEM_TYPE
                        shared_read_only_regs.append(mem_dec[2] + '0')
                        shared_read_only_regs.append(mem_dec[2] + '0')
                        shared_read_only_regs.append(mem_dec[2] + '0')
                    else:
                        type_map[mem_dec[2]] = STATE_TYPES.REG_TYPE
                    continue
                else:
                    multi_shared_pattern = re.compile(STATE_RE_EXP.MULTI_SHARED_RE_EXP)
                    match_pointer = multi_shared_pattern.match(mem_dec[4])
                    if match_pointer == None:
                        # See TODO.
                        type_map[mem_dec[4]] = STATE_TYPES.SHARED_MEM_TYPE
                        shared_read_only_regs.append(mem_dec[4])
                    else:
                        multi_shared_name = match_pointer.group(1)
                        shared_read_only_regs.append(multi_shared_name)
                        type_map[multi_shared_name] = STATE_TYPES.SHARED_MEM_TYPE
            if a[0] == PTX_DECL_TYPE.LOCAL:
                local_dec = a
                multi_local_pattern = re.compile(STATE_RE_EXP.MULTI_LOCAL_RE_EXP)
                match_pointer = multi_local_pattern.match(local_dec[4])
                if match_pointer == None:
                    # See TODO.
                    type_map[local_dec[4]] = STATE_TYPES.LOCAL_MEM_TYPE
                    local_regs.append(local_dec[4])
                else:
                    multi_local_name = match_pointer.group(1)
                    num = int(match_pointer.group(2))
                    local_regs.append(multi_local_name)
                    type_map[multi_local_name] = STATE_TYPES.LOCAL_MEM_TYPE
    
    ##########################################################################################
    ############## Split opcode&operands, clear parenthesis ##################################
    ##########################################################################################
    
    process_code_split = []
    for i in range(len(process_code)):
        a = re.split(STATE_RE_EXP.CODE_SPLIT_RE_EXP, process_code[i])
        a = filter(lambda a: a != '', a)
        process_code[i] = a
    
    reg_map = {}
    parenthesis_re = re.compile(STATE_RE_EXP.PARENTHESIS_RE_EXP)
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
        if (opcode_split[0] == PTX_MEM_INST.LD_PARAM_A):
            if (opcode_split[1] == PTX_MEM_INST.LD_PARAM_B):
                if(opcode_split[2][-2:] == PTX_MEM_INST.LD_PARAM_C):
                    process_code[i] = []
                    shared_read_only_regs.append(process_code_line[1])
    
    ##########################################################################################
    ############## Store Parameter Regs       ################################################
    ############## Store General&Special Regs ################################################
    ##########################################################################################
     
    shared_read_only_obj = open(TMP_DIR + DECL_FILE.SHARED_READONLY_REGFILE, 'w')
    pickle.dump(shared_read_only_regs, shared_read_only_obj)
    shared_read_only_obj.close()
    local_regs_obj = open(TMP_DIR + DECL_FILE.LOCAL_REGFILE, 'w')
    pickle.dump(local_regs, local_regs_obj)
    local_regs_obj.close()
    
    declaration_file = 'ptx_declaration_file'
    declaration_obj = open(TMP_DIR + declaration_file, 'w')
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
        if len(process_code_line) > EFF_PARAMETER.USELESS_CODE_LENGTH:
            opcode = process_code_line[0]
            #find all ld addresses
            if opcode[:2] == PTX_MEM_INST.LD_INST:
                if opcode.find(PTX_MEM_INST.LD_ACQ_INST) != -1:
                    addr = process_code_line[1]
                else:
                    addr = process_code_line[2]
                if addr.find('+') != -1:
                    addr = addr[:addr.find('+')]
                if addr not in addr_dest:
                    if addr[0] == '%':
                        addr_dest.append(addr)
            #find all st
            if opcode[:2] == PTX_MEM_INST.ST_INST:
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
            if opcode[:4] == PTX_MEM_INST.ATOM_INST:
                addr = process_code_line[2]
                if addr.find('+') != -1:
                    addr = addr[:addr.find('+')]
                if addr not in addr_dest:
                    if addr[0] == '%':
                        addr_dest.append(addr)
    
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
                    continue
            new_process_code.append(process_code_line)
    print len(new_process_code)
    print line_num
    ptx_program_file = 'ptx_program'
    ptx_program_obj = open(TMP_DIR + ptx_program_file, 'w')
    pickle.dump(new_process_code, ptx_program_obj)
    
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
        zero_starter.append(process_code_line[1])
    zero_starter_obj = open(TMP_DIR + 'zero_starter', 'w')  
    pickle.dump(zero_starter, zero_starter_obj)
    zero_starter_obj.close()              
