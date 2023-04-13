#!/bin/bash
#SBATCH --job-name=redflag
#SBATCH --output=/nobackup1/vilgalys/logs/redflag_out.txt
#SBATCH -e /nobackup1/vilgalys/logs/redflag_error.txt
#SBATCH -p sched_mit_sloan_interactive
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=120GB
#SBATCH --time=4-00:00:00

cd ~
module load python/3.9.4
python3 -m venv mypy
source ~/mypy/bin/activate/
which python
if [[ $PATH == *":/home/vilgalys/.local/bin"* ]]; then
  echo $PATH
else
  PATH=$PATH:/home/vilgalys/.local/bin
fi
pip3 install --quiet -r /pool001/vilgalys/pickles/requirements.p
cd /nobackup1/vilgalys/

python3 /pool001/vilgalys/inferring_expectations/code/data_processing/download_cal_gridmet.py
python3 /pool001/vilgalys/inferring_expectations/code/data_processing/merge_gridmet_redflag.py
python3 /pool001/vilgalys/inferring_expectations/code/data_processing/merge_gridmet_locations.py
