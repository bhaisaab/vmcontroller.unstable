#!python
# To run from the root folder:
#   trial tests/
import sys
import os

# When executed from the root folder
sys.path.append(os.path.abspath("./tests"))
sys.path.append(os.path.abspath("./src/vmcontroller.common"))
sys.path.append(os.path.abspath("./src/vmcontroller.host"))
sys.path.append(os.path.abspath("./src/vmcontroller.vm"))
# Just in case executed inside the tests/ folder
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("../src/vmcontroller.common"))
sys.path.append(os.path.abspath("../src/vmcontroller.host"))
sys.path.append(os.path.abspath("../src/vmcontroller.vm"))

# Add here test modules
from test_config import *
