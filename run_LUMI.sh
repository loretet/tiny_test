#!/bin/bash -l
#SBATCH --job-name=test_00
#SBATCH --account=project_465002526
#SBATCH --time=0-20:17:00              
#SBATCH --partition=standard-g
#SBATCH --nodes=12              # n. of nodes = ntasks/8. Modify only this for bigger runs
#SBATCH --ntasks-per-node=8    # don't change this, it must be == to --gpus-per-node
#SBATCH --gpus-per-node=8      # don't change this, it must be == to --ntasks-per-node  
#SBATCH --cpus-per-task=7      # n. of processessors per task. Don't change this, it must be >= OMP_NUM_THREADS        

casename="lat15_deg00_"
mesh="n80"

CASE_FILE="${casename}.case"
MESH_FILE="/scratch/project_465002526/lorenzol/meshes/${mesh}.nmsh"
NEKO_EXEC="neko_${casename}"
OUTPUT_DIR="/scratch/project_465002526/lorenzol/coriolis/${mesh}/${casename}/"
LOG_DIR="/scratch/project_465002526/lorenzol/coriolis/${mesh}/logfiles/"

echo "Running Neko with the following settings:"
echo "  Job Name: $SLURM_JOB_NAME"
echo "  Account: $SLURM_ACCOUNT"
echo "  Time Limit: $SLURM_TIME"    
echo "  Partition: $SLURM_PARTITION"
echo "  Nodes: $SLURM_NNODES"
echo "  Tasks per Node: $SLURM_NTASKS_PER_NODE"
echo "  GPUs per Node: $SLURM_GPUS_PER_NODE"
echo "  CPUs per Task: $SLURM_CPUS_PER_TASK"
echo "  "
echo "  Case File: $CASE_FILE"
echo "  Neko Executable: $NEKO_EXEC"
echo "  Output Directory: $OUTPUT_DIR"

ml CrayEnv cce/19.0.0 craype-accel-amd-gfx90a rocm/6.3.4 cray-python

# Load modules for the GNU CPU environment
# # OPENMP BUG FIX! # #
ml PrgEnv-gnu cray-mpich/9.0.1
ml craype-accel-amd-gfx90a rocm/6.3.4

export OMP_NUM_THREADS=2
export MPICH_GPU_SUPPORT_ENABLED=1
export NEKO_GS_STRTGY=3
export JSON_INSTALL=/users/lorenzol/json-fortran/b
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${JSON_INSTALL}/lib64/
export PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:${JSON_INSTALL}/lib64/pkgconfig
export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH

if [ "$SLURM_NTASKS_PER_NODE" -ne "$SLURM_GPUS_PER_NODE" ]; then
    echo "Error: Rank-to-GPU mismatch. Tasks: $SLURM_NTASKS_PER_NODE, GPUs: $SLURM_GPUS_PER_NODE"
    echo "--ntasks-per-node must be == to --gpus-per-node"   
    exit 1 
fi

if [ "$OMP_NUM_THREADS" -gt "$SLURM_CPUS_PER_TASK" ]; then
    echo "Error: OMP_NUM_THREADS ($OMP_NUM_THREADS) exceeds CPUs per task ($SLURM_CPUS_PER_TASK)."
    echo "#SBATCH -c must be >= OMP_NUM_THREADS"
    exit 1
fi

if [ "$SLURM_NNODES" -lt 2 ]; then
    BIND_SETTING="cores" 
    echo "Small case detected. Using automated core binding."
else
    BIND_SETTING="mask_cpu:7e000000000000,7e00000000000000,7e0000,7e000000,7e,7e00,7e00000000,7e0000000000"
    echo "Large case detected. Applying optimized hex masks."
fi

if [ ! -d $LOG_DIR ]; then
    mkdir $LOG_DIR
fi

if [ ! -d ${OUTPUT_DIR} ]; then
    mkdir ${OUTPUT_DIR}
fi

ml list

cat << EOF > select_gpu
#!/bin/bash

export ROCR_VISIBLE_DEVICES=\$SLURM_LOCALID
exec \$*
EOF

chmod +x ./select_gpu

d="$(date +%F_%H-%M-%S)"

sed -i "s|\"output_directory\":.*|\"output_directory\": \"$OUTPUT_DIR\",|g" "$CASE_FILE"
sed -i "s|\"mesh_file\":.*|\"mesh_file\": \"$MESH_FILE\",|g" "$CASE_FILE"
SBATCH_TIME=$(grep "#SBATCH --time=" "$0" | cut -d'=' -f2)
sed -i "s|\"job_timelimit\":.*|\"job_timelimit\": \"$SBATCH_TIME\",|g" "$CASE_FILE"

srun -u --cpu-bind=${BIND_SETTING},verbose ./select_gpu ./${NEKO_EXEC} ${CASE_FILE} > $LOG_DIR/log.run_$casename 2>&1

rm -rf ./select_gpu
mv *0.* ${OUTPUT_DIR}
./users/lorenzol/scripts/clean_csv.sh ${OUTPUT_DIR}
