import sys

if sys.version_info[0] < 3:
    raise ImportError('Python < 3 is unsupported.')
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise ImportError('Python < 3.6 is unsupported.')
