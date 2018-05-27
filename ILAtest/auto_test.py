import os
import time
file_obj = open('rodinia_test_list')
test_length = {}
test_length["bfs_kernel"] = "148"
test_length["bfs_kernel2"] = "24"
test_length["backprop_cuda_kernel"] = "200"
test_length["backprop_cuda_kernel2"] = "46"
test_length["hotspot"] = "180"
test_length["lavamd"] = "388" 
test_length["nn_cuda"] = "24"
test_length["needle_kernel"] = "425"
test_length["needle_kernel2"] = "428"
test_length["kmeans_cuda"] = "38"
test_length["kmeans_cuda2"] = "45"
test_length["partical_naive"] = "68"
test_length["pathfinder"] = "106"
test_length["hashtable_kernel"] = "70"
effective_length_file = "effective_length.result"
effective_length = open(effective_length_file, "w")
effective_length.write("effective_length:\n")
effective_length.close()

while 1:
    line = file_obj.readline()
    print line
    if not line:
        break
    os.popen("python ptx_tokenizer.py " + line[:-1] + ".ptx >> " + effective_length_file)
    '''
    time.sleep(3)
    os.popen("python ptx_ld_set.py")
    time.sleep(3)
    os.popen("python ptx_init.py " + line[:-1])
    time.sleep(3)
    a = open('run_test.slurm', 'r')
    code = a.readlines()
    a.close()
    code[-1] = "python ptxILAdirect_nd_sync_at_bar.py " + test_length[line[:-1]] + " > " + line[:-1] + ".result128g"
    a = open('run_test.slurm', 'w')
    a.writelines(code)
    a.close()
    time.sleep(3)
    os.popen("sbatch run_test.slurm")
    time.sleep(3)
    '''
