import ila
import time
import pickle
import Instruction_Format
import re
import sys
ila.setloglevel(3, '')
ila.enablelog('BMCResult')
FILE_DIR = 'files/'
TMP_DIR = 'tmp/'
ptx_declaration_obj = open(TMP_DIR + 'ptx_declaration_file', 'r')
ptx_declaration = pickle.load(ptx_declaration_obj)
print ptx_declaration
program_obj = open(TMP_DIR + 'ptx_program', 'r')
program = pickle.load(program_obj)
instruction_format = Instruction_Format.InstructionFormat()


class barSpec(object):
    def __init__(self):
        self.BAR_INIT = 0
        self.BAR_ENTER = 1
        self.BAR_WAIT = 2
        self.BAR_EXIT = 3
        self.BAR_FINISH = 4
        self.BAR_COUNTER_ENTER_BITS = 32
        self.BAR_COUNTER_EXIT_BITS = 32
        self.BAR_STATE_BITS = 3
        self.THREAD_NUM = 2
        self.BAR_OPCODE = 71


class ptxGPUModel(object):
    def __init__(self):
        self.model = ila.Abstraction('GPU_ptx')
        self.debug_log = {}
        self.bar_spec = barSpec()
        self.thread_num = 2
        self.createStates()
        self.add_assumptions()
        #self.ubar()
         
    def createStates(self):
        self.pc_list = []   #Two pc
        self.pc_next_list = []    #Two pc's next state function
        #self.imem_list = []
        self.next_state_dict = {}   #For next state function
        self.pred_registers = []    
        self.scalar_registers = []
        self.long_scalar_registers = []
        self.log_register = self.model.reg('log_register', instruction_format.LONG_REG_BITS)
        self.check_register = self.model.reg('check_register', instruction_format.LONG_REG_BITS)
        self.en_log_register = self.model.reg('en_log_register', 1)
        self.en_check_register = self.model.reg('en_check_register', 1)
        self.lsg_log_register = self.model.reg('lsg_log_register', 2)
        self.lsg_check_register = self.model.reg('lsg_check_register', 2)
        self.log_atom_flag_register = self.model.reg('log_atom_flag_register', 1)
        self.check_atom_flag_register = self.model.reg('check_atom_flag_register', 1)
        self.mflag_log_register = self.model.reg('mflag_log_register', 1)
        self.mflag_check_register = self.model.reg('mflag_check_register', 1)
        self.mguard_log_register = self.model.reg('mguard_log_register', instruction_format.LONG_REG_BITS)
        self.mguard_check_register = self.model.reg('mguard_check_register', instruction_format.LONG_REG_BITS)
        self.mutex_flag_list = []
        self.mutex_guard_list = []
        self.mutex_flag_next_list = []
        self.mutex_guard_next_list = []
        for i in range(2):
            self.mutex_flag_list.append(self.model.reg('mutex_flag_%d' % (i), 1))
            self.mutex_guard_list.append(self.model.reg('mutex_guard_%d' % (i), instruction_format.LONG_REG_BITS))
            self.mutex_flag_next_list.append(self.mutex_flag_list[i])
            self.mutex_guard_next_list.append(self.mutex_guard_list[i])
      
        #next state functions for monitors.
        self.mflag_log_register_next_cond = ila.bool(False)
        self.mflag_check_register_next_cond = ila.bool(False)
        self.mguard_log_register_next = self.mguard_log_register
        self.mguard_check_register_next = self.mguard_check_register
        self.log_register_next = self.log_register
        self.en_log_register_next = self.en_log_register
        self.lsg_log_register_next = self.lsg_log_register
        self.check_register_next = self.check_register
        self.en_check_register_next = self.en_check_register
        self.lsg_check_register_next = self.lsg_check_register
        self.log_atom_flag_register_next = self.log_atom_flag_register
        self.check_atom_flag_register_next = self.check_atom_flag_register
        self.arb_fun_list = [self.model.fun('arb_fun_0', 1, []), self.model.fun('arb_fun_1', 1, [])]
        self.arb_list = [ila.appfun(self.arb_fun_list[0], []), ila.appfun(self.arb_fun_list[1], [])]
        self.arb_data_fun_list = [self.model.fun('arb_data_fun_0', instruction_format.LONG_REG_BITS ,[]), self.model.fun('arb_data_fun_1', instruction_format.LONG_REG_BITS ,[])]
        self.arb_data_list = [ila.appfun(self.arb_data_fun_list[0]), ila.appfun(self.arb_data_fun_list[1])]
        self.bar_arrive_inst = []
        self.bar_sync_inst = []
        self.bar_aux_inst = []
        self.bar_sync_list = []
        self.bar_arrive_list = []
        self.bar_aux_list = []
        self.createPC()
        
        self.createRegs(0)
        self.createRegs(1)
        self.createConst()
        self.bar_state_list = []
 
        self.generate_next_state(0)
        self.generate_next_state(1)
 
        self.createLog()
        self.createCheck()

        self.set_next_state()
        self.set_next_pc(0)
        self.set_next_pc(1)
        #self.createuBar()
        #self.addInstruction()

    def createPC(self):
        self.pc_list.append(self.model.reg('pc_0' , instruction_format.PC_BITS))
        self.pc_next_list.append(self.pc_list[0] + 4)
        self.pc_list.append(self.model.reg('pc_1', instruction_format.PC_BITS))
        self.pc_next_list.append(self.pc_list[1] + 4)

    def createRegs(self, index):
        for reg_name in ptx_declaration.keys():
            reg_type = ptx_declaration[reg_name]
            if isinstance(reg_type, tuple):
                continue
            if reg_type == '.pred':
                self.pred_registers.append(self.model.reg(reg_name + '_%d' %(index), instruction_format.PRED_REG_BITS))
                self.next_state_dict[reg_name + '_%d' %(index)] = self.pred_registers[-1]
                continue
            reg_len = int(reg_type[2:])
            if reg_len == 32:
                self.scalar_registers.append(self.model.reg(reg_name + '_%d' %(index), instruction_format.REG_BITS))
                self.next_state_dict[reg_name + '_%d' %(index)] = self.scalar_registers[-1]
            elif reg_len == 8:
                temp_reg = self.model.reg(reg_name + '_%d' %(index), 8)
                self.next_state_dict[reg_name + '_%d' % (index)] = temp_reg
            elif reg_len == 16:
                temp_reg = self.model.reg(reg_name + '_%d' %(index), 16)
                self.next_state_dict[reg_name + '_%d' % (index)] = temp_reg
 
            else:
                self.long_scalar_registers.append(self.model.reg(reg_name + '_%d' %(index), instruction_format.LONG_REG_BITS))# we don't have 64 bits constant 
                self.next_state_dict[reg_name + '_%d' %(index)] = self.long_scalar_registers[-1]

    def createConst(self):
        self.pred_one = ila.const(0x1, instruction_format.PRED_REG_BITS)
        self.pred_zero = ila.const(0x0, instruction_format.PRED_REG_BITS)
    
    def create_data_race_element(self, access_set, log, lsg_update, atom):
        if log == True:
            suffix = 'log'
            index = 0
        else:
            suffix = 'check'    
            index = 1 

        self.log_clean = ila.bool(False)
        self.check_clean = ila.bool(False)
        for pc in self.bar_sync_list:
            self.log_clean = self.log_clean | ((self.pc_list[0] == pc) & (self.pc_list[1] == pc))
            self.check_clean = self.check_clean | ((self.pc_list[0] == pc) & (self.pc_list[1] == pc))

        ctaidx_0 = self.model.getreg('%ctaid.x_0')
        ctaidx_1 = self.model.getreg('%ctaid.x_1')
        ctaidy_0 = self.model.getreg('%ctaid.y_0')
        ctaidy_1 = self.model.getreg('%ctaid.y_1')
        self.log_clean = (self.log_clean) & ((ctaidx_0 == ctaidx_1) & (ctaidy_0 == ctaidy_1))
        self.check_clean = (self.check_clean) & ((ctaidx_0 == ctaidx_1) & (ctaidy_0 == ctaidy_1))
        for pc in access_set.keys():
            reg_name = access_set[pc]
            operands = re.split('\+', reg_name)
            reg_len = 64
            print operands
            for i in range(len(operands)):
                operand = operands[i]
                if operand in ptx_declaration.keys():
                    op_reg_type = ptx_declaration[operand]
                    op_reg_len = int(op_reg_type[2:])
                    if op_reg_len < reg_len:
                        operands[i] = ila.sign_extend(self.model.getreg(operand + '_%d' % (index)), reg_len)
                    else:
                        operands[i] = self.model.getreg(operand + '_%d' % (index))
                else:
                    operands[i] = self.aux_imm(operand, 0, reg_len)

            access_reg_next = operands[0]
            for i in range(1, len(operands)):
                access_reg_next = access_reg_next + operands[i]

            en_access_reg_next = ila.const(0x1, 1)
            en_access_reg_clear = ila.const(0x0, 1)
            if log:
                self.log_register_next = ila.ite((self.pc_list[0] == pc) & (self.arb_list[index] == 1), access_reg_next, self.log_register_next)
                self.en_log_register_next = ila.ite((self.pc_list[0] == pc) & (self.arb_list[index] == 1), en_access_reg_next, self.en_log_register_next)
                self.lsg_log_register_next = ila.ite((self.pc_list[0] == pc) & (self.arb_list[index] == 1), lsg_update, self.lsg_log_register_next)
                self.mflag_log_register_next_cond = ((self.arb_list[index] == 1) & (self.pc_list[0] == pc)) | self.mflag_log_register_next_cond
                if atom:
                    self.log_atom_flag_register_next = ila.ite((self.pc_list[0] == pc) & (self.arb_list[index] == 1), ila.const(0x1, 1), self.log_atom_flag_register_next)
                else:
                    self.log_atom_flag_register_next = ila.ite((self.pc_list[0] == pc) & (self.arb_list[index] == 1), ila.const(0x0, 1), self.log_atom_flag_register_next)

            else:
                self.check_register_next = ila.ite((self.pc_list[1] == pc) & (self.arb_list[index] == 1), access_reg_next, self.check_register_next)
                self.en_check_register_next = ila.ite((self.pc_list[1] == pc) & (self.arb_list[index] == 1), en_access_reg_next, self.en_check_register_next)
                self.lsg_check_register_next = ila.ite((self.pc_list[1] == pc) & (self.arb_list[index] == 1), lsg_update, self.lsg_check_register_next)
                self.mflag_check_register_next_cond = ((self.arb_list[index] == 1) & (self.pc_list[1] == pc)) | self.mflag_check_register_next_cond
                if atom:
                    self.check_atom_flag_register_next = ila.ite((self.pc_list[1] == pc) & (self.arb_list[index] == 1), ila.const(0x1, 1), self.check_atom_flag_register_next)
                else:
                    self.check_atom_flag_register_next = ila.ite((self.pc_list[1] == pc) & (self.arb_list[index] == 1), ila.const(0x0, 1), self.check_atom_flag_register_next)
 
        if log:
            self.en_log_register_next = ila.ite(self.log_clean, ila.const(0x0, 1), self.en_log_register_next)
        else:
            self.en_check_register_next = ila.ite(self.check_clean, ila.const(0x0, 1), self.en_check_register_next)
 

    def createLog(self):
        s_ld_set_file = 's_ld_set'
        s_ld_set_obj = open(TMP_DIR + s_ld_set_file, 'r')
        s_ld_set = pickle.load(s_ld_set_obj)
        s_ld_set_obj.close()
        g_ld_set_file = 'g_ld_set'
        g_ld_set_obj = open(TMP_DIR + g_ld_set_file, 'r')
        g_ld_set = pickle.load(g_ld_set_obj)
        g_ld_set_obj.close()
        l_ld_set_file = 'l_ld_set'
        l_ld_set_obj = open(TMP_DIR + l_ld_set_file, 'r')
        l_ld_set = pickle.load(l_ld_set_obj)
        l_ld_set_obj.close()
        g_atom_set_file = 'g_atom_set' 
        g_atom_set_obj = open(TMP_DIR + g_atom_set_file, 'r')
        g_atom_set = pickle.load(g_atom_set_obj)
        s_atom_set_file = 's_atom_set'
        s_atom_set_obj = open(TMP_DIR + s_atom_set_file, 'r')
        s_atom_set = pickle.load(s_atom_set_obj)
         
        g_st_set_file = 'g_st_set'
        g_st_set_obj = open(TMP_DIR + g_st_set_file, 'r')
        g_st_set = pickle.load(g_st_set_obj)
        g_st_set_obj.close()
        s_st_set_file = 's_st_set'
        s_st_set_obj = open(TMP_DIR + s_st_set_file, 'r')
        s_st_set = pickle.load(s_st_set_obj)
        s_st_set_obj.close()
        l_st_set_file = 'l_st_set'
        l_st_set_obj = open(TMP_DIR + l_st_set_file, 'r')
        l_st_set = pickle.load(l_st_set_obj)
        l_st_set_obj.close()

        for pc in g_st_set.keys():
            g_ld_set[pc] = g_st_set[pc]
        for pc in s_st_set.keys():
            s_ld_set[pc] = s_st_set[pc]
        for pc in l_st_set.keys():
            l_ld_set[pc] = l_st_set[pc]
        self.create_data_race_element(g_ld_set, True, ila.const(0x2, 2), 0)
        self.create_data_race_element(s_ld_set, True, ila.const(0x1, 2), 0)
        self.create_data_race_element(l_ld_set, True, ila.const(0x0, 2), 0)
        self.create_data_race_element(g_atom_set, True, ila.const(0x2, 2), 1)
        self.create_data_race_element(s_atom_set, True, ila.const(0x1, 2), 1)

    def createCheck(self):
        g_st_set_file = 'g_st_set'
        g_st_set_obj = open(TMP_DIR + g_st_set_file, 'r')
        g_st_set = pickle.load(g_st_set_obj)
        g_st_set_obj.close()
        s_st_set_file = 's_st_set'
        s_st_set_obj = open(TMP_DIR + s_st_set_file, 'r')
        s_st_set = pickle.load(s_st_set_obj)
        s_st_set_obj.close()
        l_st_set_file = 'l_st_set'
        l_st_set_obj = open(TMP_DIR + l_st_set_file, 'r')
        l_st_set = pickle.load(l_st_set_obj)
        l_st_set_obj.close()
        g_atom_set_file = 'g_atom_set' 
        g_atom_set_obj = open(TMP_DIR + g_atom_set_file, 'r')
        g_atom_set = pickle.load(g_atom_set_obj)
        s_atom_set_file = 's_atom_set'
        s_atom_set_obj = open(TMP_DIR + s_atom_set_file, 'r')
        s_atom_set = pickle.load(s_atom_set_obj)
    
        self.create_data_race_element(g_st_set, False, ila.const(0x2, 2), 0)
        self.create_data_race_element(s_st_set, False, ila.const(0x1, 2), 0)
        self.create_data_race_element(l_st_set, False, ila.const(0x0, 2), 0)
        self.create_data_race_element(g_atom_set, False, ila.const(0x2, 2), 1)
        self.create_data_race_element(s_atom_set, False, ila.const(0x1, 2), 1)


    def aux_dest(self, opcode, src_list, index):
        dest = None
        opcode_split = re.split('\.', opcode)
        opcode_name = opcode_split[0]
        if opcode_name == 'mov':
            dest = src_list[0]
        if opcode_name == 'and':
            dest = src_list[0] & src_list[1]
        if opcode_name == 'cvta':
            dest = src_list[0]
        if opcode_name == 'cvt':
            dest = src_list[0]
        if opcode_name == 'shr':
            dest = ila.ashr(src_list[0], src_list[1])
        if opcode_name == 'shl':
            dest = src_list[0] << src_list[1]
        if opcode_name == 'add':
            dest = src_list[0] + src_list[1]
        if opcode_name == 'sub':
            dest = src_list[0] - src_list[1]
        if opcode_name == 'or':
            dest = src_list[0] | src_list[1]
        if opcode_name == 'ld':
            dest = self.arb_data_list[index]
        if opcode_name == 'atom':
            dest = self.arb_data_list[index]
        if opcode_name == 'mul':
            opcode_width = opcode_split[1]
            op_len = int(opcode_split[-1][1:])
            if opcode_width == 'wide':
                src0 = ila.sign_extend(src_list[0], op_len * 2)
                src1 = ila.sign_extend(src_list[1], op_len * 2)
                dest = src0 * src1
            elif opcode_width == 'lo':
                src0 = ila.sign_extend(src_list[0], op_len * 2)
                src1 = ila.sign_extend(src_list[1], op_len * 2)
                dest_long = src0 * src1
                dest = dest_long[(op_len - 1):0]
            else:
                src0 = ila.sign_extend(src_list[0], op_len * 2)
                src1 = ila.sign_extend(src_list[1], op_len * 2)
                dest_long = src0 * src1
                dest = dest_long[(op_len - 1):0]
        if opcode_name == 'mad':
            opcode_width = opcode_split[1]
            op_len = int(opcode_split[2][1:])
            if opcode_width == 'lo':
                src0 = ila.sign_extend(src_list[0], op_len * 2)
                src1 = ila.sign_extend(src_list[1], op_len * 2)
                src2 = ila.sign_extend(src_list[2], op_len * 2)
                dest_long = src0 * src1 + src2
                dest = dest_long[(op_len - 1) : 0]
        if opcode_name == 'fma':
            opcode_width = opcode_split[1]
            op_len = int(opcode_split[2][1:])
            if opcode_width == 'rn':
                src0 = ila.sign_extend(src_list[0], op_len * 2)
                src1 = ila.sign_extend(src_list[1], op_len * 2)
                src2 = ila.sign_extend(src_list[2], op_len * 2)
                dest_long = src0 * src1 + src2
                dest = dest_long[(op_len - 1) : 0]
        if opcode_name == 'sqrt':
            dest = src_list[0]
        if opcode_name == 'setp':
            opcode_cmp = opcode_split[1]
            if opcode_cmp == 'eq':
                dest = ila.ite(src_list[0] == src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'ne':
                dest = ila.ite(src_list[0] != src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'gt':
                dest = ila.ite(src_list[0] > src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'lt':
                dest = ila.ite(src_list[0] < src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'le':
                dest = ila.ite((src_list[0] < src_list[1]) | (src_list[0] == src_list[1]), self.pred_one, self.pred_zero)
            if opcode_cmp == 'ge':
                dest = ila.ite((src_list[0] > src_list[1]) | (src_list[0] == src_list[1]), self.pred_one, self.pred_zero)
            if opcode_cmp == 'ltu':
                dest = self.arb_list[index]  

        if opcode_name == 'bar':
            if opcode_split[1] == 'arrive':
                self.bar_arrive_inst[index] = self.bar_arrive_inst[index] | (self.pc_list[index] == self.current_pc)
                if self.current_pc not in self.bar_arrive_list:
                    self.bar_arrive_list.append(self.current_pc)
            elif opcode_split[1] == 'sync':
                self.bar_sync_inst[index] = self.bar_sync_inst[index] | (self.pc_list[index] == self.current_pc)
                if self.current_pc not in self.bar_sync_list:
                    self.bar_sync_list.append(self.current_pc)
            else:
                self.bar_aux_inst[index] = self.bar_aux_inst[index] | (self.pc_list[index] == self.current_pc)
                if self.current_pc not in self.bar_aux_list:
                    self.bar_aux_list.append(self.current_pc)
        return dest


    def adjust_dest(self, index, dest, dest_str, op_len):
        dest_type = ptx_declaration[dest_str]
        if dest_type == '.pred':
            return dest
        else:
            dest_len = int(dest_type[2:])
            if dest_len > op_len:
                return ila.sign_extend(dest, dest_len)
            elif dest_len < op_len:
                return dest[(dest_len - 1) : 0]
            else:
                return dest


    def perform_instruction(self, index, program_line, pc_target):
            if len(program_line) < 2:
                self.debug_log[self.current_pc] = program_line
                return
            opcode = program_line[0]
            opcode_split = re.split('\.', opcode)
            opcode_name = opcode_split[0]
            if (index == 0):
                print program_line
                print self.current_pc
            if (opcode_name != '@') & (opcode_name != 'bra'):
                self.next_state_finished.append(program_line[1])
                if opcode_name == 'bar':
                    op_len = 0
                    dest = self.aux_dest(program_line[0], [], index)
                    self.current_pc += 4
                    return
                elif opcode == 'ld.acq':
                    lock_addr_name = program_line[1]
                    lock_addr_reg = self.model.getreg(lock_addr_name + '_%d' % (index))
                    lock_addr_type = ptx_declaration[lock_addr_name]
                    op_len = int(lock_addr_type[2:])
                    if op_len < instruction_format.LONG_REG_BITS:
                        lock_addr_reg = ila.zero_extend(lock_addr_reg, instruction_format.LONG_REG_BITS)
                    self.mutex_guard_next_list[index] = ila.ite(self.pc_list[index] == self.current_pc, lock_addr_reg, self.mutex_guard_next_list[index])
                    self.mutex_flag_next_list[index] = ila.ite(self.pc_list[index] == self.current_pc, self.model.const(0x1, 1), self.mutex_flag_next_list[index])
                    self.current_pc += 4
                    return
                elif opcode == 'st.rel':
                    self.mutex_flag_next_list[index] = ila.ite(self.pc_list[index] == self.current_pc, self.model.const(0x1, 1), self.mutex_flag_next_list[index])
                    self.current_pc += 4
                    return 
                else:
                    if opcode_split[-1] == 'pred':
                        op_len = 1
                    elif opcode_split[-1] == 'ca':
                        op_len = int(opcode_split[-2][1:])
                    elif opcode_split[-1] == 'cg':
                        op_len = int(opcode_split[-2][1:])
                    else:
                        op_len = int(opcode_split[-1][1:])
                src_list = []
                for i in range(2, len(program_line)):
                    src_str = program_line[i]
                    src_components = re.split('\+', src_str)
                    for i in range(len(src_components)):
                        src_component = src_components[i]
                        src_components[i] = self.aux_imm(src_component, index, op_len)
                    src_sum = src_components[0]
                    for i in range(1, len(src_components)):
                        src_sum = src_sum + src_components[0]
                    src_list.append(src_sum)
                dest = self.aux_dest(program_line[0], src_list, index)
                if not dest:
                    self.debug_log[self.current_pc] = program_line
                    self.current_pc += 4
                    return
                dest_str = program_line[1]
                if opcode.find('atom') != -1:
                    dest_str = program_line[1]
                    op_len = instruction_format.LONG_REG_BITS
                if opcode.find('ld') != -1:
                    if opcode.find('param') != -1:
                        self.current_pc += 4
                        return
                    if opcode.find('v4') != -1:
                        self.current_pc += 4
                        return
                    dest_str = program_line[1]
                    op_len = instruction_format.LONG_REG_BITS
                dest = self.adjust_dest(index, dest, dest_str, op_len)
                current_next_state = self.next_state_dict[dest_str + '_%d' % (index)]
                self.next_state_dict[dest_str + '_%d' % (index)] = ila.ite(self.pc_list[index] == self.current_pc, dest, current_next_state)
                self.current_pc += 4
                return 
            else:
                if (opcode_name == '@'):
                    opcode_jmp_dest = program_line[3]
                    pred_guard = self.pred_one
                    pred_guard_reg = program_line[1]
                    if program_line[1][0] == '!':
                        pred_guard = self.pred_zero
                        pred_guard_reg = program_line[1][1:] 
                    opcode_pred = self.model.getreg(pred_guard_reg + '_%d' % (index))
                    opcode_jmp_target = pc_target[opcode_jmp_dest]
                    print opcode
                    print opcode_jmp_target
                    pc_jmp = ila.ite(opcode_pred == pred_guard, ila.const(opcode_jmp_target, instruction_format.PC_BITS), self.pc_list[index] + 4)
                elif(opcode_name == 'bra'):
                    opcode_jmp_dest = program_line[1]
                    opcode_jmp_target = pc_target[opcode_jmp_dest]
                    print opcode
                    print opcode_jmp_target
                    pc_jmp = ila.const(opcode_jmp_target, instruction_format.PC_BITS)
                self.pc_next_list[index] = ila.ite(self.pc_list[index] == self.current_pc, pc_jmp, self.pc_next_list[index])
                self.current_pc += 4
 
 
    def generate_next_state(self, index):
        instruction_book_obj = open(FILE_DIR + 'instruction_book', 'r')
        instruction_book = instruction_book_obj.readlines()
        self.next_state_finished = []
        pc_target = {}
        self.current_pc = 0
        self.bar_sync_inst.append(ila.bool(False))
        self.bar_aux_inst.append(ila.bool(False))
        self.bar_arrive_inst.append(ila.bool(False))
        for program_line in program:
            if len(program_line) < 2:
                if len(program_line) == 0:
                    continue
                if program_line[0][-1] == ':':
                    pc_target[program_line[0][:-1]] = self.current_pc 
            else:
                self.current_pc += 4
                
        print pc_target
        print self.current_pc
        self.current_pc = 0
        for program_line in program:
            current_pc_in = self.current_pc
            self.perform_instruction(index, program_line, pc_target)
        for reg_name in ptx_declaration.keys():
            if reg_name not in self.next_state_finished:
                reg = self.model.getreg(reg_name + '_%d' %(index))
                self.model.set_next(reg_name + '_%d' %(index), reg)
        self.pc_max = self.current_pc

 
    def set_next_state(self):
        # reg next state
        for state_name in self.next_state_dict.keys():
            index = int(state_name[-1])
            self.model.set_next(state_name, self.next_state_dict[state_name])
        self.model.set_next('log_register', self.log_register_next)
        self.model.set_next('check_register', self.check_register_next)
        self.model.set_next('en_log_register', self.en_log_register_next)
        self.model.set_next('en_check_register', self.en_check_register_next)
        self.model.set_next('lsg_log_register', self.lsg_log_register_next)
        self.model.set_next('lsg_check_register', self.lsg_check_register_next)
        self.model.set_next('mflag_log_register', ila.ite(self.mflag_log_register_next_cond, self.mutex_flag_list[0], self.mflag_log_register))
        self.model.set_next('mguard_log_register', ila.ite(self.mflag_log_register_next_cond, self.mutex_guard_list[0], self.mguard_log_register))
        self.model.set_next('mflag_check_register', ila.ite(self.mflag_check_register_next_cond, self.mutex_flag_list[1], self.mflag_check_register))
        self.model.set_next('mguard_check_register', ila.ite(self.mflag_check_register_next_cond, self.mutex_guard_list[1], self.mguard_check_register))
        self.model.set_next('mutex_flag_0', self.mutex_flag_next_list[0])
        self.model.set_next('mutex_flag_1', self.mutex_flag_next_list[1])
        self.model.set_next('mutex_guard_0', self.mutex_guard_next_list[0])
        self.model.set_next('mutex_guard_1', self.mutex_guard_next_list[1])
        self.model.set_next('log_atom_flag_register', self.log_atom_flag_register_next)
        self.model.set_next('check_atom_flag_register', self.check_atom_flag_register_next)

    def set_next_pc(self, index):
        self.pc_wait = ((self.bar_sync_inst[index]) | (self.bar_arrive_inst[index]) | (self.bar_aux_inst[index])) & (~(self.bar_sync_inst[1 - index])) & (~(self.bar_arrive_inst[1 - index])) & (~(self.bar_aux_inst[1 - index]))
        self.model.set_next('pc_%d' % (index) , ila.ite(self.pc_list[index] < (self.pc_max), ila.ite(self.pc_wait, self.pc_list[index], self.pc_next_list[index]), self.pc_list[index]))
    
    def add_assumptions(self):
        ptx_declaration_diff_obj = open(TMP_DIR + 'diff_read_only_regs', 'r')
        ptx_declaration_diff = pickle.load(ptx_declaration_diff_obj)
        ptx_declaration_shared_obj = open(TMP_DIR + 'shared_readonly_regs', 'r')
        ptx_declaration_shared = pickle.load(ptx_declaration_shared_obj)
        ptx_parameter_regs_obj = open(TMP_DIR + 'parameter_regs', 'r')
        ptx_parameter_regs = pickle.load(ptx_parameter_regs_obj)
        ptx_buildin_regs_obj = open(TMP_DIR + 'buildin_regs', 'r')
        ptx_buildin_regs = pickle.load(ptx_buildin_regs_obj)
        ptx_shared_read_only_range_regs_obj = open(TMP_DIR + 'shared_read_only_range_regs', 'r')
        ptx_shared_read_only_range_regs = pickle.load(ptx_shared_read_only_range_regs_obj)
        ptx_zero_starter_obj = open(TMP_DIR + 'zero_starter', 'r')
        ptx_zero_starter = pickle.load(ptx_zero_starter_obj)
        self.init = ila.bool(True) 
        pc = self.model.getreg('pc_0')
        self.init = self.init & (pc == self.model.const(0x0, instruction_format.PC_BITS))
        pc = self.model.getreg('pc_1')
        self.init = self.init & (pc == self.model.const(0x0, instruction_format.PC_BITS))
        i = 1
        for reg_name in ptx_declaration_shared:
            reg0 = self.model.getreg(reg_name + '_%d' % (0))
            reg1 = self.model.getreg(reg_name + '_%d' % (1))
            self.init = self.init & (reg0 == reg1)
            operand_type = ptx_declaration[reg_name]
            operand_len = int(operand_type[2:])
            if operand_len < 64:
                self.init_max = self.model.const(i, instruction_format.REG_BITS) << 27
                self.init_range = self.model.const(1, instruction_format.REG_BITS) << 26
                self.init = self.init & (reg0 == (self.init_max - self.init_range))
                i += 1
                continue
            self.init_max = self.model.const(i, instruction_format.LONG_REG_BITS) << 59
            self.init_range = self.model.const(1, instruction_format.LONG_REG_BITS) << 58
            self.init = self.init & (reg0 == (self.init_max - self.init_range))
            i += 1
        self.diff = ila.bool(False)
        self.diff_range = ila.bool(True)
        for reg in ptx_declaration_diff.keys():
            reg0 = self.model.getreg(reg + '_%d' %(0))
            reg1 = self.model.getreg(reg + '_%d' %(1))
            v = ptx_declaration_diff[reg]
            self.diff = self.diff | (reg0 != reg1)
            self.diff_range = self.diff_range & (reg0 < v) & (reg1 < v) & (reg0 >= 0) & (reg1 >= 0)
        self.init = self.init & self.diff_range & self.diff

        for reg in ptx_parameter_regs.keys():
            reg0 = self.model.getreg(reg + '_%d' % (0))
            reg1 = self.model.getreg(reg + '_%d' % (1))
            v = ptx_parameter_regs[reg]
            self.init = self.init & (reg0 == v) & (reg1 == v)

        for reg in ptx_buildin_regs.keys():
            reg0 = self.model.getreg(reg + '_%d' % (0))
            reg1 = self.model.getreg(reg + '_%d' % (1))
            v = ptx_buildin_regs[reg]
            self.init = self.init & (reg0 == v) & (reg1 == v)
        
        for reg in ptx_shared_read_only_range_regs.keys():
            reg0 = self.model.getreg(reg + '_%d' % (0))
            reg1 = self.model.getreg(reg + '_%d' % (1))
            v = ptx_shared_read_only_range_regs[reg]
            self.init = self.init & (reg0 > 0) & (reg0 <v) & (reg0 == reg1)
        
        for reg in ptx_zero_starter:
            reg0 = self.model.getreg(reg + '_%d' % (0))
            reg1 = self.model.getreg(reg + '_%d' % (1))
            self.init = self.init & (reg0 == 0) & (reg1 == 0) 

        for reg in self.pred_registers:
            self.init = self.init & (reg == self.pred_one)
        self.init = self.init & (self.en_log_register == 0) & (self.en_check_register == 0) & (self.log_atom_flag_register == 0) & (self.check_atom_flag_register == 0)
        self.init = self.init & (self.mutex_flag_list[0] == 0) & (self.mutex_flag_list[1] == 0) & (self.mflag_log_register == 0) & (self.mflag_check_register == 0)
        tidx0 = self.model.getreg('%tid.x_0')
        tidx1 = self.model.getreg('%tid.x_1')
        tidy0 = self.model.getreg('%tid.y_0')
        tidy1 = self.model.getreg('%tid.y_1')
        tidz0 = self.model.getreg('%tid.z_0')
        tidz1 = self.model.getreg('%tid.z_1')
        ctaidx0 = self.model.getreg('%ctaid.x_0')
        ctaidx1 = self.model.getreg('%ctaid.x_1')
        ctaidy0 = self.model.getreg('%ctaid.y_0')
        ctaidy1 = self.model.getreg('%ctaid.y_1')
        ctaidz0 = self.model.getreg('%ctaid.z_0')
        ctaidz1 = self.model.getreg('%ctaid.z_1')
 
        # Imply with no warp
        self.imply =(~((self.log_atom_flag_register == 1) & (self.check_atom_flag_register == 1))) & (self.check_register == self.log_register) & (self.en_log_register == 1) & (self.en_check_register == 1) & (((self.lsg_log_register == 2) & (self.lsg_check_register == 2)) | ((self.lsg_log_register == 1) & (self.lsg_check_register == 1) & (ctaidx0 == ctaidx1) & (ctaidy0 == ctaidy1) & (ctaidz0 == ctaidz1) )) #& (~((ctaidx0 == ctaidx1) & ((tid0 >> 5) == (tid1 >> 5)))) 
 #& (ctaidx0 == ctaidx1) & (ctaidy0 == ctaidy1)))  #& ((tid0 >> 5) != (tid1 >> 5))

        # Imply with warp
        # self.imply = (self.imply) | ((self.log_register_next != self.log_register) & (self.check_register_next != self.check_register) & (self.check_register_next == self.log_register_next) & (self.en_log_register_next == 1) & (self.en_check_register_next == 1) & (((self.lsg_log_register_next == 2) & (self.lsg_check_register_next == 2)) | ((self.lsg_log_register_next == 1) & (self.lsg_check_register_next == 1))) & (ctaidx0 == ctaidx1) & ((tid0 >> 5) == (tid1 >> 5))) #& (ctaidx0 == ctaidx1) & (ctaidy0 == ctaidy1)))  #& ((tid0 >> 5) != (tid1 >> 5))
 
        # Imply with rel acq
        self.imply = self.imply & (~((self.mflag_log_register == 1) & (self.mflag_check_register == 1) & (self.mguard_log_register == self.mguard_check_register)))


        self.predicate_bit = self.model.bit('predicate_bit')  
        #self.model.set_init('predicate_bit', self.model.bool(True))
        self.init = self.init & (self.predicate_bit == self.model.bool(True))
        self.model.set_next('predicate_bit', ila.ite(self.imply, self.model.bool(False), self.predicate_bit))
        
    def aux_imm(self, operand_str, index, op_len):
        if operand_str in ptx_declaration.keys():
            operand = self.model.getreg(operand_str + '_%d' % (index))
            operand_type = ptx_declaration[operand_str]
            if operand_type == '.pred':
                operand_length = instruction_format.PRED_REG_BITS
            else: 
                operand_length = int(operand_type[2:])
            if operand_length < op_len:
                return ila.sign_extend(operand, op_len)
            elif operand_length > op_len:
                return operand[(op_len - 1) : 0]
            else:
                return operand
        else:
            try:
                operand_int = int(operand_str)
            except ValueError:
                operand_int = 0
            if operand_int < 0:
                operand_int = -operand_int
                operand = (self.model.const(1, op_len) << (op_len - 1)) - self.model.const(operand_int, op_len) + (self.model.const(1, op_len) << (op_len - 1))
            else:
                operand = self.model.const(operand_int, op_len)
            return operand


if __name__ == '__main__':
    ptx = ptxGPUModel()
    time_consumption = []
    result = []
    start = time.clock()
    print ptx.model.bmcCond(ptx.predicate_bit == ila.bool(True), int(sys.argv[1]), ptx.init)
    end = time.clock()
    print end-start
 
# TODO(Yue Xing): store this into a struct.
# Reference code length:
# bfs_kernel:148
# bfs_kernel2:24
# backprop_kernel:100
# backprop_kernel2:46
# hotspot:180
# lavamd:388
# needle1:425
# needle2:428
# kmeans1:38
# kmeans2:45
# Particle_naive:68
# pathfinder: 246
# hashtable:35->70
# volume:66
 
