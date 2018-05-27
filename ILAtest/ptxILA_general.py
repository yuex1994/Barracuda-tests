import ila
import time
import pickle
import Instruction_Format
import re
ila.setloglevel(3, '')
ila.enablelog('BMCResult')
ptx_declaration_obj = open('ptx_declaration_file', 'r')
ptx_declaration = pickle.load(ptx_declaration_obj)
print ptx_declaration
program_obj = open('ptx_add_neighbor', 'r')
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
        self.bar_spec = barSpec()
        self.thread_num = 2
        self.createStates()
        self.add_assumptions()
        #self.ubar()
         
    def createStates(self):
        self.pc_list = []   #Two pc
        self.pc_next_list = []    #Two pc's next state function
        self.imem = self.model.mem('imem', 32, 64)

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
        #next state functions for monitors.
        self.log_register_next = self.log_register
        self.en_log_register_next = self.en_log_register
        self.lsg_log_register_next = self.lsg_log_register
        self.check_register_next = self.check_register
        self.en_check_register_next = self.en_check_register
        self.lsg_check_register_next = self.lsg_check_register

        self.arb_fun_list = [self.model.fun('arb_fun_0', 1, []), self.model.fun('arb_fun_1', 1, [])]
        self.arb_list = [ila.appfun(self.arb_fun_list[0], []), ila.appfun(self.arb_fun_list[1], [])]
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
 
        self.instFetch()
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
            else:
                self.long_scalar_registers.append(self.model.reg(reg_name + '_%d' %(index), instruction_format.LONG_REG_BITS))# we don't have 64 bits constant 
                self.next_state_dict[reg_name + '_%d' %(index)] = self.long_scalar_registers[-1]

    def createConst(self):
        self.pred_one = ila.const(0x1, instruction_format.PRED_REG_BITS)
        self.pred_zero = ila.const(0x0, instruction_format.PRED_REG_BITS)
    
    def create_data_race_element(self, log):
        if log == True:
            index = 0
            bar_pass = ((self.is_bar_list[0]) & (self.is_bar_list[1]))
            mem_lsg_type = self.fetch_inst_list[index][(instruction_format.MEM_LSG_TOP - 1) : instruction_format.MEM_LSG_BOT]
            is_log_mem_access = (self.is_ld_list[index]) | (self.is_st_list[index])
            src0_long_flag = self.src0_long_list[index]
            sreg0_index = self.sreg0_index_list[index]
            sreg0_scalar_reg = self.get_scalar_reg(sreg0_index)
            sreg0_long_scalar_reg = self.get_long_scalar_reg(sreg0_index)
            sreg0 = ila.ite(src0_long_flag, sreg0_long_scalar_reg[(instruction_format.DMEM_BITS - 1) : 0], sreg0_scalar_reg)
            imm_addr = ila.sign_extend(self.imm_list[index], instruction_format.DMEM_BITS)
            mem_address = sreg0 + imm_addr
            #Assume ld/st 32bits address
     
            log_register_next = ila.ite(is_log_mem_access, ila.ite(self.arb_list[index] == 1, mem_address, self.log_register), self.log_register)
            en_log_register_next = ila.ite(bar_pass, ila.bool(False), ila.ite(is_log_mem_access, ila.ite(self.arb_list[index] == 1, ila.bool(True), en_log_register), en_log_register))
            lsg_log_register_next = ila.ite(is_log_mem_access, ila.ite(self.arb_list[index] == 1, mem_lsg_type, lsg_log_register), lsg_log_register)
            self.model.set_next('log_regiseter', log_register_next)
            self.model.set_next('en_log_register', en_log_register_next)
            self.model.set_next('lsg_log_register', lsg_log_register_next)
        else:
            index = 1
            bar_pass = ((self.is_bar_list[0]) & (self.is_bar_list[1]))
            mem_lsg_type = self.fetch_inst_list[index][(instruction_format.MEM_LSG_TOP - 1) : instruction_format.MEM_LSG_BOT]
            is_check_mem_access = (self.is_st_list[index])
            src0_long_flag = self.src0_long_list[index]
            sreg0_index = self.sreg0_index_list[index]
            sreg0_scalar_reg = self.get_scalar_reg(sreg0_index)
            sreg0_long_scalar_reg = self.get_long_scalar_reg(sreg0_index)
            sreg0 = ila.ite(src0_long_flag, sreg0_long_scalar_reg[(instruction_format.DMEM_BITS - 1) : 0], sreg0_scalar_reg)
            imm_addr = ila.sign_extend(self.imm_list[index], instruction_format.DMEM_BITS)
            mem_address = sreg0 + imm_addr
            #Assume ld/st 32bits address
     
            check_register_next = ila.ite(is_check_mem_access, ila.ite(self.arb_list[index] == 1, mem_address, self.check_register), self.check_register)
            en_check_register_next = ila.ite(bar_pass, ila.bool(False), ila.ite(is_check_mem_access, ila.ite(self.arb_list[index] == 1, ila.bool(True), en_check_register), en_check_register))
            lsg_check_register_next = ila.ite(is_check_mem_access, ila.ite(self.arb_list[index] == 1, mem_lsg_type, lsg_check_register), lsg_check_register)
            self.model.set_next('check_register', check_register_next)
            self.model.set_next('en_check_register', en_check_register_next)
            self.model.set_next('lsg_check_register'. lsg_check_register_next)
            

 

 
 
 
    def createLog(self):
        self.create_data_race_element(True)

    def createCheck(self):
        self.create_data_race_element(False)

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
        if opcode_name == 'shr':
            dest = ila.ashr(src_list[0], src_list[1])
        if opcode_name == 'shl':
            dest = src_list[0] << src_list[1]
        if opcode_name == 'add':
            dest = src_list[0] + src_list[1]
        if opcode_name == 'sub':
            dest = src_list[0] - src_list[1]
        if opcode_name == 'mul':
            opcode_width = opcode_split[1]
            op_len = int(opcode_split[2][1:])
            if opcode_width == 'wide':
                src0 = ila.sign_extend(src_list[0], op_len * 2)
                src1 = ila.sign_extend(src_list[1], op_len * 2)
                dest = src0 * src1
            elif opcode_width == 'lo':
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
        if opcode_name == 'setp':
            opcode_cmp = opcode_split[1]
            if opcode_cmp == 'ne':
                dest = ila.ite(src_list[0] != src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'gt':
                dest = ila.ite(src_list[0] > src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'lt':
                dest = ila.ite(src_list[0] < src_list[1], self.pred_one, self.pred_zero)
            if opcode_cmp == 'le':
                dest = ila.ite((src_list[0] < src_list[1]) | (src_list[0] == src_list[1]), self.pred_one, self.pred_zero)
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
            #TODO: pc_next when bar
            
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

    def instFetch(self):
        self.fetch_list = []
        self.fetch_list.append(self.imem[ila.zero_extend(pc[0][31:2])])
        self.fetch_list.append(self.imem[ila.zero_extend(pc[1][31:2])])

    def preDecode(self):
        self.opcode_list = []
        self.is_mov_list = []
        self.is_and_list = []
        self.is_cvta_list = []
        self.is_shr_list = []
        self.is_shl_list = []
        self.is_add_list = []
        self.is_sub_list = []
        self.is_mul_list = []
        self.is_mad_list = []
        self.is_setp_list = []
        self.is_bar_list = []
        self.is_bra_list = []
        self.is_ld_list = []
        self.is_st_list = []
        self.dreg_index_list = []
        self.sreg0_index_list = []
        self.sreg1_index_list = []
        self.sreg2_index_list = []
        self.pred_index_list = []
        self.pred_enable_list = []
        self.mul_op_list = []
        self.dst_long_list = []
        self.src0_long_list = []
        self.src1_long_list = []
        self.src2_long_list = []
        self.imm_list = []
    

    def instDecode(self, index):
        #TODO: instruction_map.
        self.opcode_list.append(self.fetch_list[index][instruction_format.OPCODE_BIT_TOP:instruction_format.OPCODE_BIT_BOT])
        self.is_mov_list.append(self.opcode_list[index] == instruction_map['mov']) 
        self.is_and_list.append(self.opcode_list[index] == instruction_map['and'])
        self.is_cvta_list.append(self.opcode_list[index] == instruction_map['cvta'])
        self.is_shr_list.append(self.opcode_list[index] == instruction_map['shr'])
        self.is_shl_list.append(self.opcode_list[index] == instruction_map['shl'])
        self.is_add_list.append(self.opcode_list[index] == instruction_map['add'])
        self.is_sub_list.append(self.opcode_list[index] == instruction_map['sub'])
        self.is_mul_list.append(self.opcode_list[index] == instruction_map['mul'])
        self.is_mad_list.append(self.opcode_list[index] == instruction_map['mad'])
        self.is_setp_list.append(self.opcode_list[index] == instruction_map['setp'])
        self.is_bar_list.append(self.opcode_list[index] == instruction_map['bar'])
        self.is_bra_list.append(self.opcode_list[index] == instruction_map['bra'])
        self.is_ld_list.append(self.opcode_list[index] == instruction_map['ld'])
        self.is_st_list.append(self.opcode_list[index] == instruction_map['st'])

        self.dreg_index_list.append(self.fetch_list[index][instruction_format.DST_BIT_TOP:instruction_format.DST_BIT_BOT])
        self.sreg0_index_list.append(self.fetch_list[index][instruction_format.SRC0_BIT_TOP:instruction_format.SRC0_BIT_BOT])
        self.sreg1_index_list.append(self.fetch_list[index][instruction_format.SRC1_BIT_TOP:instruction_format.SRC1_BIT_BOT])
        self.sreg2_index_list.append(self.fetch_list[index][instruction_format.SRC2_BIT_TOP:instruction_format.SRC2_BIT_BOT])
        self.pred_enable_list.append(self.fetch_list[index][instruction_format.PRED_BIT_TOP:instruction_format.PRED_BIT_BOT])
        self.pred_index_list.append(self.fetch_list[index][instruction_format.PRED_REG_TOP:instruction_format.PRED_REG_BOT])
        self.mul_op_list.append(self.fetch_list[index][instruction_format.MUL_OP_TOP:instruction_format.MUL_OP_BOT])
        self.dst_long_list.append(self.fetch_list[index][instruction_format.DST_LONG])
        self.src0_long_list.append(self.fetch_list[index][instruction_format.SRC0_LONG])
        self.src1_long_list.append(self.fetch_list[index][instruction_format.SRC1_LONG])
        self.src2_long_list.append(self.fetch_list[index][instruction_format.SRC2_LONG])
        self.imm_list.append(self.fetch_list[index][(instruction_format.IMM_BIT_TOP - 1) : instruction_format.IMM_BIT_BOT])
        


    def get_scalar_reg(self, idx, index):
        ret = self.scalar_registers[0]
        for i in range(len(self.scalar_registers[index])):
            ret = ila.ite(i == idx, self.scalar_registers[index][i], ret)
        return ret

    def get_long_scalar_reg(self, idx):
        ret = self.long_scalar_registers[0]
        for i in range(len(self.long_scalar_registers[index])):
            ret = ila.ite(i == idx, self.long_scalar_registers[index][i], ret)
        return ret

    def get_predicate_reg(self, idx, index):
        ret = self.pred_registers[0]
        for i in range(len(self.pred_registers[index])):
            ret = ila.ite(i == idx, self.pred_registers[index][i], ret)
        return ret

           
            

    def generate_next_state(self, index):
        dreg_index = self.dreg_index_list[index]
        sreg0_index = self.sreg0_index_list[index]
        sreg1_index = self.sreg1_index_list[index]
        sreg2_index = self.sreg2_index_list[index]
        pred_enable = self.pred_enable_list[index]
        pred_index = self.pred_index_list[index]
        mul_op = self.mul_op_list[index]
        dst_long_flag = self.dst_long_list[index]
        src0_long_flag = self.src0_long_list[index]
        src1_long_flag = self.src1_long_list[index]
        src2_long_flag = self.src2_long_list[index]

        dreg_scalar_reg = self.get_scalar_reg(dreg_index)
        dreg_long_scalar_reg = self.get_long_scalar_reg(dreg_index)
        sreg0_scalar_reg = self.get_scalar_reg(sreg0_index)
        sreg0_long_scalar_reg = self.get_long_scalar_reg(sreg0_index)
        sreg1_scalar_reg = self.get_scalar_reg(sreg1_index)
        sreg1_long_scalar_reg = self.get_long_scalar_reg(sreg1_index)
        sreg2_scalar_reg = self.get_scalar_reg(sreg2_index)
        sreg2_long_scalar_reg = self.get_long_scalar_reg(sreg2_index)
        dreg = ila.ite(dst_long_flag, dreg_long_scalar_reg, ila.sign_extend(dst_scalar_reg, instruction_format.LONG_REG_BITS))
        sreg0 = ila.ite(src0_long_flag, sreg0_long_scalar_reg, ila.sign_extend(sreg0_scalar_reg, instruction_format.LONG_REG_BITS))
        sreg1 = ila.ite(sreg1_long_flag, sreg1_long_scalar_reg, ila.sign_extend(sreg1_scalar_reg, instruction_format.LONG_REG_BITS))
        sreg2 = ila.ite(sreg2_long_flag, sreg2_long_scalar_reg, ila.sign_extend(sreg2_scalar_reg, instruction_format.LONG_REG_BITS))
        #Generate Ret Expression
        mov_ret_long = sreg0
        mov_ret = mov_ret_long[(instruction_format.REG_BITS - 1) : 0]
        cvta_ret_long = sreg0 
        cvta_ret = sreg0[(instruction_format.REG_BITS - 1) : 0]
        and_ret_long = sreg0 & sreg1
        and_ret = and_result[(instruction_format.REG_BITS - 1) : 0]
        shr_ret_long = ila.ashr(sreg0, sreg1)
        shr_ret = shr_result[(instruction_format.REG_BITS - 1) : 0]
        shl_result = sreg0 << sreg1
        shl_ret = shl_result[(instruction_format.REG_BITS - 1) : 0]
        add_result = sreg0 + sreg1
        add_ret = add_result[(instruction_format.REG_BITS - 1) : 0]
        sub_result = sreg0 - sreg1
        sub_ret = sub_result[(instruction_format.REG_BITS - 1) : 0]
        mul_wide_ret = sreg0 * sreg1
        mul_lo_result = sreg0 * sreg1
        mul_lo_ret = mul_lo_result[(instruction_format.REG_BITS - 1) : 0]
        mad_wide_ret = sreg0 * sreg1 + sreg2
        mad_lo_result = sreg0 * sreg1 + sreg2
        mad_lo_ret = mad_lo_result[(instruction_format.REG_BITS - 1) : 0]
        ne_ret = (sreg0 != sreg1)
        gt_ret = (sreg0 > sreg1)
        lt_ret = (sreg0 < sreg1)
        le_ret = (sreg0 < sreg1) | (sreg0 == sreg1)

        next_state_long = ila.ite(self.is_mov_list[index], mov_ret_long, 
        ila.ite(self.is_cvta_list[index], cvta_ret_long, 
        ila.ite(self.is_and_list[index], and_ret_long, 
        ila.ite(self.is_shr_list[index], shr_ret_long,
        ila.ite(self.is_shl_list[index], shl_ret_long,
        ila.ite(self.is_add_list[index], add_ret_long,
        ila.ite(self.is_sub_list[index], sub_ret_long,
        ila.ite(self.is_mul_list[index], mul_wide_ret,
        ila.ite(self.is_mad_list[index], mad_wide_ret, dreg_long_scalar_reg)))))))))

        next_state = ila.ite(self.is_mov_list[index], mov_ret, 
        ila.ite(self.is_cvta_list[index], cvta_ret, 
        ila.ite(self.is_and_list[index], and_ret, 
        ila.ite(self.is_shr_list[index], shr_ret,
        ila.ite(self.is_shl_list[index], shl_ret,
        ila.ite(self.is_add_list[index], add_ret,
        ila.ite(self.is_sub_list[index], sub_ret,
        ila.ite(self.is_mul_list[index], mul_wide_ret,
        ila.ite(self.is_mad_list[index], mad_wide_ret, dreg_scalar_reg)))))))))
        #TODO: scalar_registers, and long_scalar_registers should be 2-D
        #ptx_reg_name_list add, pred_reg_next
        for i in range(len(self.scalar_registers[index])):
            this_reg = self.model.getreg(ptx_sreg_name_list[i] + '_%d' % (index))
            self.model.set_next(ptx_reg_name_list[i] + '_%d' % (index), ila.ite(dst_long_flag, this_reg, 
            ila.ite(dreg_index == i, 
            next_state, this_reg)))

        for i in range(len(self.long_scalar_registers[index])):
            this_reg = self.model.getreg(ptx_long_reg_name_list[i] + '_%d' % (index))
            self.model.set_next(ptx_long_reg_name_list[i] + '_%d' % (index), ila.ite(dst_long_flag, ila.ite(dreg_index == i, next_state_long. this_reg), this_reg))
            

    def get_next_pc(self, index):
        current_pc = self.pc_list[index]
        seq_next = current_pc + 4
        bar_stopped = ~((ila.is_bar_list[0]) & (ila.is_bar_list[1]))
        bar_next = ila.ite(bar_stopped, current_pc, current_pc + 4)
        bra_next = ila.sign_extend(self.imm_list[index], instruction_format.PC_BITS)
        pred_reg = self.get_pred_registers(self.pred_reg_list[index], index)
        pc_next = ila.ite(self.is_bra_list[index], 
        ila.ite(self.pred_enable_list[index] == 0, bra_next, 
        ila.ite(self.pred_enable_list[index] == 1, ila.ite(pred_reg == ila.const(0x1, 1), bra_next, seq_next), 
        ila.ite(self.pred_enable_list[index] == 2, ila.ite(pred_reg == ila.const(0x1, 1), seq_next, bra_next)))), 
        ila.ite(self.is_bar_list[index], bar_next, 
        ila.ite(current_pc >= max_pc, current_pc, seq_next)))
        self.model.set_next('pc_%d' % (index), pc_next)


    def set_next_state(self):
        self.model.set_next('log_register', self.log_register_next)
        self.model.set_next('check_register', self.check_register_next)
        self.model.set_next('en_log_register', self.en_log_register_next)
        self.model.set_next('en_check_register', self.en_check_register_next)
        self.model.set_next('lsg_log_register', self.lsg_log_register_next)
        self.model.set_next('lsg_check_register', self.lsg_check_register_next)

    def set_next_pc(self, index):
        self.pc_wait = ((self.bar_sync_inst[index]) | (self.bar_arrive_inst[index]) | (self.bar_aux_inst[index])) & (~(self.bar_sync_inst[1 - index])) & (~(self.bar_arrive_inst[1 - index])) & (~(self.bar_aux_inst[1 - index]))
        self.model.set_next('pc_%d' % (index) , ila.ite(self.pc_list[index] < (self.pc_max), ila.ite(self.pc_wait, self.pc_list[index], self.pc_next_list[index]), self.pc_list[index]))
    
    def add_assumptions(self):
        ptx_declaration_diff_obj = open('diff_read_only_regs', 'r')
        ptx_declaration_diff = pickle.load(ptx_declaration_diff_obj)
        ptx_declaration_shared_obj = open('shared_read_only_regs', 'r')
        ptx_declaration_shared = pickle.load(ptx_declaration_shared_obj)
        ptx_parameter_regs_obj = open('parameter_regs', 'r')
        ptx_parameter_regs = pickle.load(ptx_parameter_regs_obj)
        self.init = ila.bool(True) 
        pc = self.model.getreg('pc_0')
        self.init = self.init & (pc == self.model.const(0x0, instruction_format.PC_BITS))
        pc = self.model.getreg('pc_1')
        self.init = self.init & (pc == self.model.const(0x0, instruction_format.PC_BITS))
        i = 1
        for reg_name in ptx_declaration_shared:
            #TODO: change this in future.
            #if reg_name[0] == '%':
            #    continue 
            reg0 = self.model.getreg(reg_name + '_%d' % (0))
            reg1 = self.model.getreg(reg_name + '_%d' % (1))
            self.init = self.init & (reg0 == reg1)
            operand_type = ptx_declaration[reg_name]
            operand_len = int(operand_type[2:])
            if operand_len < 64:
                self.init_max = self.model.const(i, instruction_format.REG_BITS) << 27
                self.init_range = self.model.const(1, instruction_format.REG_BITS) << 26
                self.init = self.init & (reg0 < self.init_max) & (reg0 > (self.init_max - self.init_range))
                i += 1
                continue
            self.init_max = self.model.const(i, instruction_format.LONG_REG_BITS) << 59
            self.init_range = self.model.const(1, instruction_format.LONG_REG_BITS) << 58
            self.init = self.init & (reg0 < self.init_max) & (reg0 > (self.init_max - self.init_range))
            i += 1
        self.diff = ila.bool(False)
        self.diff_range = ila.bool(True)
        for reg in ptx_declaration_diff.keys():
            reg0 = self.model.getreg(reg + '_%d' %(0))
            reg1 = self.model.getreg(reg + '_%d' %(1))
            v = ptx_declaration_diff[reg]
            self.diff = self.diff | (reg0 != reg1)
            self.diff_range = self.diff_range & (reg0 < v) & (reg1 < v) & (reg0 >= 0) & (reg1 >= 0)
            #self.init = self.init & (reg0 != reg1) & (reg0 < 64) & (reg0 >= 0) & (reg1 < 64) & (reg1 >= 0)
        self.init = self.init & self.diff_range & self.diff

        for reg in ptx_parameter_regs.keys():
            reg0 = self.model.getreg(reg + '_%d' % (0))
            reg1 = self.model.getreg(reg + '_%d' % (1))
            v = ptx_parameter_regs[reg]
            self.init = self.init & (reg0 == v) & (reg1 == v)


            
        
        for reg in self.pred_registers:
            self.init = self.init & (reg == self.pred_one)
        self.init = self.init & (self.en_log_register == 0) & (self.en_check_register == 0)

 
        #self.condition = []
        #for index in range(self.thread_num):
        #    self.condition.append(self.pc_list[index] >= (self.pc_max)) 
        #self.constrain = self.condition[0]
        #for index in range(1, len(self.condition)):
        #    self.constrain = self.constrain & self.condition[index]
        tid0 = self.model.getreg('%tid.x_0')
        tid1 = self.model.getreg('%tid.x_1')
        #ctaidx0 = self.model.getreg('%ctaid.x_0')
        #ctaidx1 = self.model.getreg('%ctaid.x_1')
        #ctaidy0 = self.model.getreg('%ctaid.y_0')
        #ctaidy1 = self.model.getreg('%ctaid.y_1')
        #self.imply = (self.check_register == self.log_register) & (self.en_log_register == 1) & (self.en_check_register == 1) & (((self.lsg_log_register == 2) & (self.lsg_check_register == 2)) | ((self.lsg_log_register == 1) & (self.lsg_check_register == 1))) #& (ctaidx0 == ctaidx1) & (ctaidy0 == ctaidy1)))  #& ((tid0 >> 5) != (tid1 >> 5))
        self.imply = (self.pc_list[0] == 404)

     #   self.implied = self.implied & (self.mem_list[0] == self.mem_list[1])

        self.predicate_bit = self.model.bit('predicate_bit')  
        #self.model.set_init('predicate_bit', self.model.bool(True))
        self.init = self.init & (self.predicate_bit == self.model.bool(True))
        self.model.set_next('predicate_bit', ila.ite(self.imply, self.model.bool(False), self.predicate_bit))
#        self.a = self.model.reg('a', 1)
#        self.b = self.model.reg('b', 1)
#        self.model.set_next('a', ila.ite(self.pc_list[0] == 4, self.arb, self.a))
#        self.model.set_next('b', ila.ite(self.pc_list[0] == 8, self.arb, self.b))
#        self.test = ila.ite(self.pc_list[0] > 8, self.a == self.b, ila.bool(True)) 
        
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
            #print operand_str
            #print op_len
            operand_int = int(operand_str)
            if operand_int < 0:
                operand_int = -operand_int
                operand = (self.model.const(1, op_len) << (op_len - 1)) - self.model.const(operand_int, op_len) + (self.model.const(1, op_len) << (op_len - 1))
            else:
                operand = self.model.const(operand_int, op_len)
            return operand
ptx = ptxGPUModel()
time_consumption = []
result = []
start = time.clock()
print ptx.model.bmcCond(ptx.predicate_bit == ila.bool(True), 110, ptx.init)
end = time.clock()
print end-start
  
#for i in range(1, 30):
#    start = time.clock()
#    ptx.model.bmcCond(ptx.predicate_bit == ila.bool(True), i, ptx.init)
#    end = time.clock()
#    time_consumption.append(end - start)
#    r = ptx.model.bmcCond(ptx.predicate_bit == ila.bool(True), i, ptx.init)
#    result.append(r)
#print time_consumption
#print result   

#print ptx.model.bmcInit(ptx.predicate_bit == ila.bool(True), 28, True)
