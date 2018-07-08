import pickle
import sys

diff_read_only_regs_obj = open('diff_read_only_regs', 'w')



#default
################################################################
###################Def##########################################
#diff_read_only is used for id, is picked from a range.
#builin is used for number of id, which is fixed.
#parameter is a fixed number for some specific input.
#shared range is used for specific input with a given range.
diff_read_only_regs = {}
tid_x = 1
ctaid_x = 1
tid_y = 1
ctaid_y = 1
tid_z = 1
ctaid_z = 1
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
diff_read_only_regs['%tid.y'] = tid_y
diff_read_only_regs['%ctaid.y'] = ctaid_y
diff_read_only_regs['%tid.z'] = tid_z
diff_read_only_regs['%ctaid.z'] = ctaid_z
#pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
#diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
#parameter_regs_obj = open('parameter_regs', 'w')
parameter_regs = {}
#pickle.dump(parameter_regs, parameter_regs_obj)
#parameter_regs_obj.close()

#buildin_regs_obj = open('buildin_regs', 'w')
buildin_regs = {}
buildin_regs['%ntid.x'] = tid_x
buildin_regs['%ntid.y'] = tid_y
buildin_regs['%nctaid.x'] = ctaid_x
buildin_regs['%nctaid.y'] = ctaid_y
buildin_regs['%ntid.z'] = tid_z
buildin_regs['%nctaid.z'] = ctaid_z
#pickle.dump(buildin_regs, buildin_regs_obj)
#buildin_regs_obj.close()

#shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
shared_read_only_range_regs = {}
#pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
#shared_read_only_range_regs_obj.close()
##########################################################################




test_name = sys.argv[1]
#For MatrixMulInit
if test_name == 'matrixMul_kernel':
    diff_read_only_regs = {}
    tid_x = 16
    #tid_x = 32
    tid_y = 16
    ctaid_x = 1  #dimsBx, dimbsAy
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()

    parameter_regs_obj = open('parameter_regs', 'w')
    _Z13matrixMulCUDAPiS_S_ii_param_3 = 16 
    _Z13matrixMulCUDAPiS_S_ii_param_4 = 16
    parameter_regs = {}
    parameter_regs['%r15'] = _Z13matrixMulCUDAPiS_S_ii_param_3
    parameter_regs['%r16'] = _Z13matrixMulCUDAPiS_S_ii_param_4
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()
    
    buildin_regs_obj = open('buildin_regs', 'w')
    buildin_regs = {}
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%ntid.x'] = tid_x
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
    shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
 


#For nn Init
elif test_name == 'nn_cuda':
    diff_read_only_regs = {}
    tid_x = 256
    ctaid_x = 1024
    ctaid_y = 1024
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
    parameter_regs_obj = open('parameter_regs', 'w')
    parameter_regs = {}
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
    buildin_regs = {}
    buildin_regs['%nctaid.x'] = 1024
    buildin_regs['%ntid.x'] = 256
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()
    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
    shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
 

#For gaussian1 Init
elif test_name == 'gaussian_kernel1':
    diff_read_only_regs = {}
    tid_x = 512
    ctaid_x = 2
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
    #r_up = Size, r_down < Size, Size = 65536
    Size = 1024
    parameter_regs_obj = open('parameter_regs', 'w')
    parameter_regs = {}
    parameter_regs['%r2'] = Size
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
    buildin_regs = {}
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%ntid.x'] = tid_x
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
    shared_read_only_range_regs = {}
    t = 1023
    shared_read_only_range_regs['%r3'] = t
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
    
elif test_name == 'gaussian_kernel2':
#For gaussian2 Init
    diff_read_only_regs = {}
    tid_x = 4
    tid_y = 4
    ctaid_x = 256
    ctaid_y = 256
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
    #r_up = Size, r_down < Size, Size = 65536
    Size = 1024
    parameter_regs_obj = open('parameter_regs', 'w')
    parameter_regs = {}
    parameter_regs['%r5'] = Size
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
    buildin_regs = {}
    buildin_regs['%nctaid.x'] = 256
    buildin_regs['%nctaid.y'] = 256
    buildin_regs['%ntid.x'] = 4
    buildin_regs['%ntid.y'] = 4
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
    shared_read_only_range_regs = {}
    t = 1023
    shared_read_only_range_regs['%r6'] = t
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()

    '''
diff_read_only_regs = {}
tid_x = 16
tid_y = 16
ctaid_x = 1
ctaid_y = 4
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
diff_read_only_regs['%tid.y'] = tid_y
diff_read_only_regs['%ctaid.y'] = ctaid_y
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
hid = 16
parameter_regs_obj = open('parameter_regs', 'w')
parameter_regs = {}
parameter_regs['%r11'] = hid
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
buildin_regs = {}
buildin_regs['%nctaid.x'] = 1
buildin_regs['%nctaid.y'] = 4
buildin_regs['%ntid.x'] = 16
buildin_regs['%ntid.y'] = 16
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()
    '''
    '''
#base.cu
#diff_read_only_regs = {}
tid_x = 1
ctaid_x = 2
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()
    '''

#base_with_syncthreads
    '''
tid_x = 1
ctaid_x = 2
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()
    '''

#warp_lock
    '''
tid_x = 33
ctaid_x = 1
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()
    '''
#vectorAdd
elif test_name == 'vectorAdd':
    tid_x = 256
    ctaid_x = 196
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r2'] = 50000
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()

#bucketsort
elif test_name == 'bucketsort':
    tid_x = 32
    ctaid_x = 1024
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs 
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['ntid.x'] = tid_x
    buildin_regs['nctaid.x'] = ctaid_x
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
    

#Whats this
    '''
tid_x = 256
ctaid_x = 4
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
parameter_regs 
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
buildin_regs['%ntid.x'] = tid_x
buildin_regs['%nctaid.x'] = ctaid_x
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()
    '''

#warp_lock.cu
    '''
tid_x = 33
ctaid_x = 1
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%ctaid.x'] = ctaid_x
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
parameter_regs 
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
buildin_regs['%ntid.x'] = tid_x
buildin_regs['%nctaid.x'] = ctaid_x
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()
    '''
#bfs
elif test_name == 'bfs_kernel':
    tid_x = 512
    ctaid_x = 256
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r2'] = 512 * 256
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%nctaid.x'] = ctaid_x
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
elif test_name == 'bfs_kernel2':
    tid_x = 512
    ctaid_x = 256
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r2'] = 512 * 256
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%nctaid.x'] = ctaid_x
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#backprop k1
elif test_name == 'backprop_cuda_kernel':
    tid_x = 16
    tid_y = 16
    ctaid_x = 1
    ctaid_y = 4
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r8'] = 16
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()



#backprop k2
elif test_name == 'backprop_cuda_kernel2':
    tid_x = 16
    tid_y = 16
    ctaid_x = 1
    ctaid_y = 4
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r4'] = 16
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#hotspot
elif test_name == 'hotspot':
    tid_x = 16
    tid_y = 16
    ctaid_x = 43
    ctaid_y = 43
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r10'] = 512
    parameter_regs['%r11'] = 512
    parameter_regs['%r12'] = 2
    parameter_regs['%r13'] = 2
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#lavamd
elif test_name == 'lavamd':
    tid_x = 128
    tid_y = 1
    ctaid_x = 1000
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#needle
elif test_name == 'needle_kernel':
    tid_x = 16
    tid_y = 1
    ctaid_x = 64
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r9'] = 2048
    parameter_regs['%r10'] = 10
    parameter_regs['%r11'] = 64
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
elif test_name == 'needle_kernel2':
    tid_x = 16
    tid_y = 1
    ctaid_x = 64
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r9'] = 2048
    parameter_regs['%r10'] = 10
    parameter_regs['%r11'] = 64
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()

#kmeans1
elif test_name == 'kmeans_cuda':
    tid_x = 256
    tid_y = 1
    ctaid_x = 256
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r2'] = 256 * 256
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#kmeans2
elif test_name == 'kmeans_cuda2':
    tid_x = 256
    tid_y = 1
    ctaid_x = 16
    ctaid_y = 16
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r4'] = 256 * 256
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#nncuda
elif test_name == 'nn_cuda':
    tid_x = 256
    tid_y = 1
    ctaid_x = 256
    ctaid_y = 2
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r2'] = 256 * 256 * 2 - 10
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
#partical
elif test_name == 'partical_naive':
    tid_x = 128
    tid_y = 1
    ctaid_x = 8
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r5'] = 1000
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()

#pathfinder
elif test_name == 'pathfinder':
    tid_x = 256
    tid_y = 1
    ctaid_x = 463
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r12'] = 10
    parameter_regs['%r13'] = 100000
    parameter_regs['%r14'] = 0
    parameter_regs['%r15'] = 463
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
elif test_name == "hashtable_kernel":
    tid_x = 192
    tid_y = 1
    ctaid_x = 120
    ctaid_y = 1
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r3'] = 8192
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()
elif test_name == "volumeFilter_kernel":
    tid_x = 32
    tid_y = 32
    tid_z = 1
    ctaid_x = 2
    ctaid_y = 2
    ctaid_z = 2
    diff_read_only_regs['%tid.x'] = tid_x
    diff_read_only_regs['%tid.y'] = tid_y
    diff_read_only_regs['%ctaid.x'] = ctaid_x
    diff_read_only_regs['%ctaid.y'] = ctaid_y
    diff_read_only_regs['%tid.z'] = tid_z
    diff_read_only_regs['%ctaid.z'] = ctaid_z
    pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
    diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
    parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
    parameter_regs['%r6'] = 10
    pickle.dump(parameter_regs, parameter_regs_obj)
    parameter_regs_obj.close()

    buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
    buildin_regs['%ntid.x'] = tid_x
    buildin_regs['%ntid.y'] = tid_y
    buildin_regs['%ntid.z'] = tid_z
    buildin_regs['%nctaid.x'] = ctaid_x
    buildin_regs['%nctaid.y'] = ctaid_y
    buildin_regs['%nctaid.z'] = ctaid_z
    pickle.dump(buildin_regs, buildin_regs_obj)
    buildin_regs_obj.close()

    shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
    #shared_read_only_range_regs['%rd5'] = 50
    #shared_read_only_range_regs['%rd4'] = 50
    #shared_read_only_range_regs['%rd6'] = 1
    pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
    shared_read_only_range_regs_obj.close()


else:
    print("error")
    pass

#Nvidia Benchmark
'''
tid_x = 1
tid_y = 1
ctaid_x = 2
ctaid_y = 1
diff_read_only_regs['%tid.x'] = tid_x
diff_read_only_regs['%tid.y'] = tid_y
diff_read_only_regs['%ctaid.x'] = ctaid_x
diff_read_only_regs['%ctaid.y'] = ctaid_y
pickle.dump(diff_read_only_regs, diff_read_only_regs_obj)
diff_read_only_regs_obj.close()
#r_up = Size, r_down < Size, Size = 65536
parameter_regs_obj = open('parameter_regs', 'w')
#parameter_regs = {}
pickle.dump(parameter_regs, parameter_regs_obj)
parameter_regs_obj.close()

buildin_regs_obj = open('buildin_regs', 'w')
#buildin_regs = {}
buildin_regs['%ntid.x'] = tid_x
buildin_regs['%ntid.y'] = tid_y
buildin_regs['%nctaid.x'] = ctaid_x
buildin_regs['%nctaid.y'] = ctaid_y
pickle.dump(buildin_regs, buildin_regs_obj)
buildin_regs_obj.close()

shared_read_only_range_regs_obj = open('shared_read_only_range_regs', 'w')
#shared_read_only_range_regs = {}
pickle.dump(shared_read_only_range_regs, shared_read_only_range_regs_obj)
shared_read_only_range_regs_obj.close()




'''
