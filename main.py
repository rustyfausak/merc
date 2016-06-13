"""Merc

Usage:
  main.py FILE

"""
from docopt import docopt
from merc.merc import analyze

with open('VERSION') as f:
    version = f.read().strip()

args = docopt(__doc__, version=version)
analyze(args['FILE'])
