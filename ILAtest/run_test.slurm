#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=23:00:00
#SBATCH --mem=100000
python ptxILAdirect_nd_sync_at_bar.py 84 > backprop1_revised.result100g
