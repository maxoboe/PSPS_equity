#!/bin/bash
#SBATCH --job-name=regress
#SBATCH --output=/nobackup1/vilgalys/logs/regress_out.txt
#SBATCH -e /nobackup1/vilgalys/logs/regress_error.txt
#SBATCH -p sched_mit_sloan_interactive
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=100GB
#SBATCH --time=128:00:00

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
# Need to process data before running regression; this is conducted in launch_summary_scripts
python3 /pool001/vilgalys/inferring_expectations/code/regression/make_stata_input.py

module load sloan/stata/16/mp
stata-mp -b do /pool001/vilgalys/inferring_expectations/code/regression/aggregate_regression.do
stata-mp -b do /pool001/vilgalys/inferring_expectations/code/regression/ignition_probability.do
stata-mp -b do /pool001/vilgalys/inferring_expectations/code/regression/psps_decision.do
stata-mp -b do /pool001/vilgalys/inferring_expectations/code/regression/duration_customers.do