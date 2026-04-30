#!/bin/bash -l                                                                                                                   
#SBATCH -J neko_tiny_test_GPU                                                                                       
# The partition (Dardel: gpu  LUMI: dev-g for tests and standard-g or small-g for the real runs)                                                                                                                             
#SBATCH -p gpu                                                                                                                          
# 1 hour wall-clock time will be given to this job                                                                  
#SBATCH -t 0-00:05:00                                                                                                                         
#SBATCH --nodes=1                                                                                                                       
#SBATCH --ntasks-per-node=8                                                                                                             
# Keep these two options are they are:
#SBATCH --gpus-per-task=1                                                                                                                   
#SBATCH --gpu-bind=closest            
# Number of requested CPU cores:
#SBATCH -c 8            
# Project name (Dardel: naiss2025-1-5 or 2025-3-39  LUMI: project_465002526)
#SBATCH -A naiss2025-1-5

# LUMI:
# ml CrayEnv cpe/23.09 craype-accel-amd-gfx90a rocm

# Dardel:
ml craype-accel-amd-gfx90a rocm/6.3.3 PrgEnv-cray && module use /cfs/klemming/pdc/projects/hpcrd/modules && ml hpcrd json-fortran/8.3.0-cce-18.0.1-bjoug3p

if [ ! -d logfiles ]; then
    mkdir logfiles
fi

if [ ! -d output ]; then
    mkdir output
fi

# export MPICH_GPU_SUPPORT_ENABLED=1                                                                                
# export OMP_NUM_THREADS=1                                                                                          
export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}
export MPICH_GPU_SUPPORT_ENABLED=1

d="$(date +%F_%H-%M-%S)"

srun -u ./neko tiny_test.case > logfiles/logfile.log${d} 2>&1
mv *0.* output/
