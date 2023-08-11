# Code to process images. Should be run from command line targetting a specific folder

import sys
from argparse import ArgumentParser


def inputParse():
    # Eventually want to run this from the command line
    workingFolder = ""
    fileExt = ""
    nameFilter = ""
    return workingFolder, fileExt, nameFilter


def main(args) -> int:
    # User inputs
    print(args.folderName, args.fileExt, args.nameFilter)
    return 0


if __name__ == '__main__':
    parser = ArgumentParser(prog='millifluidic',
                            description='Greyscale image processing for millifluidic images',
                            epilog='Currently in development')
    parser.add_argument('folderName')
    parser.add_argument('fileExt')
    parser.add_argument('nameFilter')
    args = parser.parse_args()
    sys.exit(main(args))