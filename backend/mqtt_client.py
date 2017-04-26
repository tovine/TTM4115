import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), "RPi", "src"))
del sys.modules["mqtt_client"]#ew
from mqtt_client import *
del sys.path[0]


