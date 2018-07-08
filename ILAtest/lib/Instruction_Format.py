class InstructionFormat(object):
    def __init__(self):
        self.PC_BITS = 32
        self.INSTRUCTION_BITS = 64
        self.IMM_BIT_TOP = 64 
        self.IMM_BIT_BOT = 48
        self.MEM_LSG_TOP = 48
        self.MEM_LSG_BOT = 46
        self.PRED_OP_TOP = 46
        self.PRED_OP_BOT = 43
        self.DST_LONG = 43
        self.SRC0_LONG = 42
        self.SRC1_LONG = 41
        self.SRC2_LONG = 40
        self.MUL_OP_TOP = 39
        self.MUL_OP_BOT = 37
        self.PRED_REG_TOP = 37
        self.PRED_REG_BOT = 32
        self.PRED_REG_BITS = 1
        self.REG_BITS = 32
        self.LONG_REG_BITS = 64
        self.OPCODE_LENGTH = 32
        self.OPCODE_BIT_TOP = 32
        self.OPCODE_BIT_BOT = 22
        self.OPCODE_BIT = 22
        self.DST_BIT_TOP = 22
        self.DST_BIT_BOT = 17
        self.DST_BIT = 17
        self.SRC0_BIT_TOP = 17
        self.SRC0_BIT_BOT = 12
        self.SRC0_BIT = 12
        self.SRC1_BIT_TOP = 12
        self.SRC1_BIT_BOT = 7
        self.SRC1_BIT = 7
        self.SRC2_BIT_TOP = 7
        self.SRC2_BIT_BOT = 2
        self.SRC2_BIT = 2
        self.BASE_BIT = 2
        self.BASE_BIT_TOP = 2
        self.BASE_BIT_BOT = 1
        self.PRED_BIT_TOP = 1
        self.PRED_BIT_BOT = 0
        self.PRED_BIT = 1
        self.MEM_BITS = 64
        self.MEM_ADDRESS_BITS = 64 
        self.DMEM_BITS = 32


