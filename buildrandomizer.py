import argparse
import sys

import BuildLibs.gui
from BuildLibs import GetVersion, setVerbose


parser = argparse.ArgumentParser(description='Build Engine Randomizer')
parser.add_argument('--version', action="store_true", help='Output version')
parser.add_argument('--verbose', action="store_true", help="Output way more to the screen")
args = parser.parse_args()

if args.verbose:
    setVerbose(2)

if args.version:
    print(GetVersion())
    sys.exit(0)

BuildLibs.gui.main()
