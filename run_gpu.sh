#!/bin/bash -l                                                                                                                   
#SBATCH -J neko_tiny_test_GPU                                                                                       
# The partition                                                                                                                             
#SBATCH -p gpu                                                                                                                          
# 1 hour wall-clock time will be given to this job                                                                  
#SBATCH -t 00:05:00                                                                                                                         
#SBATCH --nodes=1                                                                                                                       
#SBATCH --ntasks-per-node=8                                                                                                             
# Keep these two options are they are:
#SBATCH --gpus-per-task=1                                                                                                                   
#SBATCH --gpu-bind=closest            
# Number of requested CPU cores:
#SBATCH -c 4                                                                                                                        
#SBATCH -A naiss2025-1-5


ml PrgEnv-cray
ml rocm/6.2.4
ml craype-accel-amd-gfx90a

if [ ! -d logfiles ]; then
    mkdir logfiles
fi

# export MPICH_GPU_SUPPORT_ENABLED=1                                                                                
# export OMP_NUM_THREADS=1                                                                                          
export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}
export MPICH_GPU_SUPPORT_ENABLED=1

d="$(date +%F_%H-%M-%S)"

srun -u ./neko tiny_test_RL.case > logfiles/logfile.log${d}
