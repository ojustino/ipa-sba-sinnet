import argparse
import copy
import json
import numpy as np
import pathlib
import pytz
import re
import shlex
import subprocess
import sys

from collections import defaultdict
from datetime import datetime as dt

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str,
                    help='The notebook file to be checked')
args = parser.parse_args()

nb_ext = '.ipynb'

try:
    nb_file = pathlib.Path(args.file)
    if not nb_file.suffix == nb_ext:
        raise ValueError(f"file extension must be {nb_ext}")

except Exception as err:
    parser.print_help()
    raise err

# create a separating line for the script file with unique text, like:
# #################################flake-8-check################################
signature = 'flake-8-check'
fill_0 = 39 - np.floor(len(signature) / 2).astype(int)
fill_1 = 39 - np.ceil(len(signature) / 2).astype(int)

separator = '# ' + '#' * fill_0 + signature + '#' * fill_1

# save relevant file paths
code_file = pathlib.Path(f"{nb_file.stem}_scripted.py")
warn_file = pathlib.Path(f"{nb_file.stem}_pep8.txt")
# flake8_file = pathlib.Path(".github/helpers/run_flake8.sh")
flake8_file = pathlib.Path("run_flake8.sh")

# save code cell contents to a script, dividing in blocks with the separator
code_cells = []
with open(nb_file) as f1:
    og_nb = json.load(f1)

    with open(code_file, 'w') as f2:
        for i, cl in enumerate(og_nb['cells']):
            if cl['cell_type'] == 'code':
                code_cells.append(i)
                for o in cl['source']:
                    f2.write(o)
                f2.write('\n' * 2)
                f2.write(separator)
                f2.write('\n') # important, file's end must be one blank line

# run flake8 and save the results to a new file
# https://stackoverflow.com/a/31995784
subprocess.call(shlex.split(f"sh {flake8_file} {code_file} {warn_file}"))

# read in the PEP8 warnings
with open(warn_file) as f3:
    warns = f3.readlines()

# if there are none, QUIT while we're ahead
if not warns:
    # print('')
    sys.exit()

# read in the script and find the lines that function as cell borders
with open(code_file) as f4:
    script = f4.readlines()

borderlines = []
for j, ll in enumerate(script):
    if re.search(f"#+{signature}#+", ll):
        borderlines.append(j)

# customize the beginning of each PEP8 warning
pre = dt.now(pytz.timezone("America/New_York")).strftime('%Y-%m-%d %H:%M:%S - INFO - ')
# pre = 'INFO:pycodestyle:'
# pre = ''

# create dict ready to take stderr dicts and append warning messages. the nested
# defaultdict guarantees a first-level key for each cell number needed, and a
# second-level list for appending 'text' strings, and nothing extra (w/o errors!)
stderr_shared = {'name': 'stderr', 'output_type': 'stream'}
nu_output_dict = defaultdict(lambda: defaultdict(list))

# match the warnings' line numbers to the notebook's cells with regex and math
for w in warns:
    # get line numbers of each warning from the script
    w = w[re.match(code_file.name, w).end():]
    loc = [int(d) for d in re.findall('(?<=:)\d+(?=:)', w)]

    # translate them into cell numbers and intra-cell line number
    code_cell_num = np.searchsorted(borderlines, loc[0])
    all_cell_num = code_cells[code_cell_num]
    line_in_cell = str(loc[0] - borderlines[code_cell_num - 1] - 1)
    # (the final minus one accounts for the buffer after the separator

    # print(f"code_cell_num {code_cell_num}, line_in_cell {line_in_cell}, "
    #       f"all_cell_num {all_cell_num}")

    # only keep line/column info and warning from original flake8 text.
    # prepend it with the customized string chosen earlier
    nu_msg = pre + re.sub(':\d+(?=:)', line_in_cell, w, count=1)

    # update the defaultdict
    nu_output_dict[all_cell_num].update({'name': 'stderr', 'output_type': 'stream'})
    nu_output_dict[all_cell_num]['text'].append(nu_msg)

# use the defaultdict's keys to learn which cells own the warnings
cells_to_edit = list(nu_output_dict.keys())
injected_nb = copy.deepcopy(og_nb)

for num, cell in enumerate(injected_nb['cells']):
    # clear any cell output, regardless of PEP8 status
    if cell.get('execution_count'):
        cell['execution_count'] = None
    if cell.get('outputs'):
        cell['outputs'] = []

    # inject PEP8 warnings into cells marked earlier
    if num in cells_to_edit:
        cell['outputs'] = [nu_output_dict[num]]

# insert cells for enabling interactive PEP8 feedback just before first code cell
flake8_magic_cells = [{
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<p style=\"font-size:200%; color:#e56020; background-color:#1d1160;\"><b><i>Reviewer note:</i> Begin PEP8 check cells (delete below when finished)</b></p>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# disable all imported packages' loggers\n",
    "import logging\n",
    "logging.root.manager.loggerDict = {}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# enable PEP8 checker for this notebook\n",
    "%load_ext pycodestyle_magic\n",
    "%flake8_on --ignore E261,E501,W291,W293\n",
    "\n",
    "# only allow the checker to throw warnings when there's a violation\n",
    "logging.getLogger('flake8').setLevel('ERROR')\n",
    "logging.getLogger('stpipe').setLevel('ERROR')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<p style=\"font-size:200%; color:#e56020; background-color:#1d1160;\"><b><i>Reviewer note:</i> Begin PEP8 check cells (delete above when finished)</b></p>"
   ]
  }]

injected_nb['cells'][code_cells[0]:code_cells[0]] = flake8_magic_cells

# save the edited notebook
with open(nb_file, 'w') as file:
    json.dump(injected_nb, file, indent=1, ensure_ascii=False)
    file.write("\n") # end with new line since json.dump doesn't
