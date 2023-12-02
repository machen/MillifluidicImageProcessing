import re
import pandas as pd
import os
import sys
from argparse import ArgumentParser

""" Should iterate through working folder using nameFilter to identify"""


def main(args)-> int:

    fileList = os.listdir(args.folderName)

    if args.nameFilter:
        filePat = re.compile(args.nameFilter)
        if filePat.groups != 2:
            raise ValueError('Name filter needs to have two regex groups, the first specifying z height, the second specifying flow rate')
    else:
        filePat = re.compile('StereoPIV_(\d+\.\d+) depth_(\d+\.\d+)mLpMin.*\.csv')

    if args.outputFolder:
        outputFolder = args.outputFolder
    else:
        outputFolder = args.folderName+os.sep+"ProcessedData"
    try:
        os.mkdir(outputFolder)
    except FileExistsError:
        print('Folder Already Exists. Continuing.')
        pass

    for file in fileList:
        x = re.search(filePat, file)
        if x:
            print(file)
            depth = float(x.group(1))
            flowRate = float(x.group(2))
            data = pd.read_csv(args.folderName+os.sep+file,
                               header=9)
            # Set Z value and flow rate
            data.loc[:, 'Z (m)[m]'] = -depth/1000
            data.loc[:, 'q [mL/min]'] = flowRate
            # Drop values where there is no vector
            # This does not work well with ParaView which needs a grid
            # zeroLengths = data.loc[data.loc[:, 'Length[m/s]'] == 0, :]
            # data.drop(zeroLengths.index, inplace=True)
            # Output data to new file, deleting the file if it already exists
            if os.path.isfile(outputFolder+os.sep+file):
                os.remove(outputFolder+os.sep+file)
            data.to_csv(outputFolder+os.sep+file, encoding='utf-16')
    return 0

if __name__ == '__main__':
    parser = ArgumentParser(prog='PIVData',
                            description='Produces Paraview Readable csvs from Dantec PIV data',
                            epilog='Currently in development')
    parser.add_argument('-f', '--folderName', type=str,
                        default="..\\SinGPIV_1\\MillifluidicDataExport")
    parser.add_argument('-r', '--nameFilter', type=str)
    parser.add_argument('-o', '--outputFolder')
    args = parser.parse_args()
    sys.exit(main(args))

