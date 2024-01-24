import sys
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import pandas as pd


class dataSet:

    def __init__(self, listing):
        self.exptName = listing.ExptName
        self.flowRate_mLpMin = listing.flowRate_mLpmin
        self.alpha = listing.alpha
        self.location = listing.location
        diffFragment = re.compile('.*DiffImage.npy')
        timeFragment = re.compile('.*elapsedTimes.npy')
        areaFragment = re.compile('.*totalAreas.npy')
        return


def main(args) -> int:
    fileData = pd.read_csv(args.fileList)
    return 0

if __name__ == '__main__':
    parser = ArgumentParser(prog='millifluidicSweep',
                            description='Tools for reloading previously analyzed data',
                            epilog='Currently in development')
    parser.add_argument('fileList')
    args = parser.parse_args()
    sys.exit(main(args))
