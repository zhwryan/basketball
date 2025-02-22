import sys
import os.path as op

root = op.dirname(op.dirname(__file__))
if root not in sys.path:
    sys.path.append(root)
