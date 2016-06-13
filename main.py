"""Merc

Usage:
  main.py FILE

"""
from docopt import docopt
from merc.merc import Merc
import time

with open('VERSION') as f:
    version = f.read().strip()

args = docopt(__doc__, version=version)
merc = Merc(args['FILE'])
start_time = time.time()
merc.analyze()
print("--- %s seconds ---" % (time.time() - start_time))
