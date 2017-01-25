"""Merc

Usage:
  main.py FILE

"""
from docopt import docopt
from merc.merc import Merc
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s.%(funcName)-15s] [%(levelname)5s] %(message)s')

with open('VERSION') as f:
    version = f.read().strip()

args = docopt(__doc__, version=version)

start_time = time.time()
logging.info("Opening file %s.." % args['FILE'])
merc = Merc(args['FILE'])
merc.process()
logging.info("Done in %s seconds." % (time.time() - start_time))
