import pickle
import re

TMP_DIR = 'tmp/'


if __name__ == '__main__':
    ptx_program_file = TMP_DIR + 'ptx_program'
    ptx_program_obj = open(ptx_program_file, 'r')
    ptx_program = pickle.load(ptx_program_obj)
    ptx_program_obj.close()

    g_ld_set = {}
    s_ld_set = {}
    l_ld_set = {}
    g_st_set = {}
    s_st_set = {}
    l_st_set = {}
    g_atom_set = {}
    s_atom_set = {}
    current_pc = 0
    pc_target = {}
    pc_start = {}
    tag_pred = {}
    for program_line in ptx_program:
        if len(program_line) >= 2:
            if program_line[0] == '@':
                dest = program_line[3]
                pc_start[program_line[3]] = current_pc
                tag_pred[program_line[3]] = program_line[1]

            current_pc += 4
        else:
            if len(program_line) == 0:
                continue
            else:
                if program_line[0][-1] == ':':
                    pc_target[program_line[0][:-1]] = current_pc

    pc = 0
    pred_map = {}
    bar_pred_map = {}
    for program_line in ptx_program:
        if len(program_line) >= 2:
            opcode = program_line[0]
            opcode_split = re.split('\.', opcode)
            if opcode_split[0] == 'ld':
                if opcode_split[1] != 'param':
                    if opcode_split[1] == 'shared':
                        s_ld_set[pc] = program_line[2]
                    if opcode_split[1] == 'global':
                        g_ld_set[pc] = program_line[2]
                    if opcode_split[1] == 'local':
                        l_ld_set[pc] = program_line[2]
                    pred_map[pc] = []
                    for tag in tag_pred.keys():
                        start = pc_start[tag]
                        target = pc_target[tag]
                        pred = tag_pred[tag]
                        if ((start < pc) & (target > pc)):
                            pred_map[pc].append(pred)
            if opcode_split[0] == 'st':
                if opcode_split[1] == 'shared':
                    s_st_set[pc] = program_line[1]
                elif opcode_split[1] == 'global':
                    g_st_set[pc] = program_line[1]
                elif opcode_split[1] == 'local': 
                    l_st_set[pc] = program_line[1]
                pred_map[pc] = []
                for tag in tag_pred.keys():
                    if ((pc_start[tag] < pc) & (pc_target[tag] > pc)):
                        pred_map[pc].append(tag_pred[tag])
#        if opcode_split[0] == 'sust':
#
#
            if opcode_split[0] == 'atom':
                if opcode_split[1] == 'shared':
                    s_atom_set[pc] = program_line[2]
                elif opcode_split[1] == 'global':
                    g_atom_set[pc] = program_line[2]
                
            if opcode_split[0] == 'bar':
                bar_pred_map[pc] = []
                for tag in tag_pred.keys():
                    if ((pc_start[tag] < pc) & (pc_target[tag] > pc)):
                        bar_pred_map[pc].append(tag_pred[tag])
            pc += 4
    print g_ld_set
    print len(g_ld_set.keys())
    print g_st_set
    print len(g_st_set.keys())
    print s_ld_set
    print len(s_ld_set.keys())
    print s_st_set
    print len(s_st_set.keys())
    print g_atom_set
    print s_atom_set
    g_ld_set_obj = open(TMP_DIR + 'g_ld_set', 'w')
    pickle.dump(g_ld_set, g_ld_set_obj)
    s_ld_set_obj = open(TMP_DIR + 's_ld_set', 'w')
    pickle.dump(s_ld_set, s_ld_set_obj)
    l_ld_set_obj = open(TMP_DIR + 'l_ld_set', 'w')
    pickle.dump(l_ld_set, l_ld_set_obj)
    g_st_set_obj = open(TMP_DIR + 'g_st_set', 'w')
    pickle.dump(g_st_set, g_st_set_obj)
    s_st_set_obj = open(TMP_DIR + 's_st_set', 'w')
    pickle.dump(s_st_set, s_st_set_obj)
    l_st_set_obj = open(TMP_DIR + 'l_st_set', 'w')
    pickle.dump(l_st_set, l_st_set_obj)
    g_atom_set_obj = open(TMP_DIR + 'g_atom_set', 'w')
    pickle.dump(g_atom_set, g_atom_set_obj)
    s_atom_set_obj = open(TMP_DIR + 's_atom_set', 'w')
    pickle.dump(s_atom_set, s_atom_set_obj)
    pred_map_obj = open(TMP_DIR + 'pred_map', 'w')
    pickle.dump(pred_map, pred_map_obj)
    bar_pred_map_obj = open(TMP_DIR + 'bar_pred_map', 'w')
    pickle.dump(bar_pred_map, bar_pred_map_obj)
    g_ld_set_obj.close()
    s_ld_set_obj.close()
    g_st_set_obj.close()
    s_st_set_obj.close()
    pred_map_obj.close()
    bar_pred_map_obj.close()


