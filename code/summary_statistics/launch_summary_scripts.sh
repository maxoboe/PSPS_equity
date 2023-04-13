#!/bin/bash
#SBATCH --job-name=summ
#SBATCH --output=/nobackup1/vilgalys/logs/summ_out.txt
#SBATCH -e /nobackup1/vilgalys/logs/summ_error.txt
#SBATCH -p sched_mit_sloan_interactive
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=100GB
#SBATCH --time=24:00:00

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
python3 /pool001/vilgalys/inferring_expectations/code/summary_statistics/summarize_psps.py
python3 /pool001/vilgalys/inferring_expectations/code/summary_statistics/make_community_plots.py
python3 pool001/vilgalys/inferring_expectations/code/summary_statistics/make_map_figure.py
python3 /pool001/vilgalys/inferring_expectations/code/regression/make_stata_input.py

module load sloan/stata/16/mp
stata-mp -b do /pool001/vilgalys/inferring_expectations/code/summary_statistics/summarize_gridmet.do
stata-mp -b do /pool001/vilgalys/inferring_expectations/code/summary_statistics/duration_socio_tab.do

