import argparse
import sys

import GUI.gui
from BuildLibs import GetVersion, setVerbose


parser = argparse.ArgumentParser(description='Build Engine Randomizer')
parser.add_argument('--version', action="store_true", help='Output version')
parser.add_argument('--verbose', action="store_true", help="Output way more to the console")
args = parser.parse_args()

if args.verbose:
    setVerbose(2)

if args.version:
    print('Build Engine Randomizer version:', GetVersion())
    print('Python version:', sys.version_info)
    sys.exit(0)

GUI.gui.main()
