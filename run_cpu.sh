#!/bin/bash -l
#SBATCH -J neko_tiny_test
#SBATCH -t 00:05:00
#SBATCH --ntasks-per-node=8
#SBATCH --nodes 1
#SBATCH -p shared
#SBATCH -A naiss2025-1-5
#SBATCH --mail-type=BEGIN,END,FAIL

# LUMI:
# ml CrayEnv cpe/23.09 craype-accel-amd-gfx90a rocm

# Dardel:
ml PrgEnv-cray rocm/6.2.4 craype-accel-amd-gfx90a

if [ ! -d logfiles ]; then
    mkdir logfiles
fi

d="$(date +%F_%H-%M-%S)"
srun -u -n 8 ./neko tiny_test.case > logfiles/logfile_${SLURM_JOB_ID}.log${d}
