"""Merc

Usage:
  main.py FILE

"""
from docopt import docopt
from merc.merc import Merc

with open('VERSION') as f:
    version = f.read().strip()

args = docopt(__doc__, version=version)
merc = Merc(args['FILE'])
merc.analyze()
