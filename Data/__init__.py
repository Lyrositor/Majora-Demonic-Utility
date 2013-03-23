# Data
# Loads Majora's Mask constant data.

import glob
import os
import yaml

DATA = {}
for filePath in glob.glob("Data/*.txt"):
    DATA[os.path.basename(filePath)[:-4]] = yaml.load(open(filePath, "r"))
