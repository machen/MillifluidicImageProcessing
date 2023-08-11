# Code to process images. Should be run from command line targetting a specific folder

import sys, os, re
from argparse import ArgumentParser
import numpy as np
import skimage as sk
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops_table
import matplotlib.pyplot as plt


def scanImages(folderName, fileExt,
               nameFilter, imageList) -> tuple[list, np.array]:
    """ Scan through image names in folderName with file
    extension fileExt and matching pattern nameFilter"""
    filePat = re.compile(nameFilter)
    os.chdir(folderName) # move to working directory
    for item in os.listdir('.'):
        # Filter on filePat and extension
        # TODO: Should handle passing no nameFilter
        if re.match(filePat, item) and item.endswith(fileExt):
            imageList.append(item)
            imageProcess(item)
    return imageList


def imageProcess(item) -> dict:
    image = imread(item, as_gray=True)
    # TODO: Should decide on correct thresholding algorithm
    # Images may need multiple thresholds to delineate surface vs bottom
    thresh = threshold_otsu(image)
    mask = image > thresh
    label_img = label(mask)
    fullProps = sk.measure.regionprops(label_img, intensity_image=image)
    fig, ax = plt.subplots()
    # Plotting to show the image,
    # TODO: Should be a flag to plot
    # TODO: What do we do with the masked images?
    # TODO: Need to filter out small objects, consider sk.morphology.white_tophat()
    ax.imshow(mask, cmap=plt.cm.gray)
    for props in fullProps:
        equivCircRad = np.sqrt(props.area)/np.pi
        y0, x0 = props.centroid
        circle = plt.Circle((x0,y0), equivCircRad, color='r',alpha=0.3)
        ax.add_patch(circle)
    return fullProps


def main(args) -> int:
    imageList = []
    scanImages(args.folderName, args.fileExt, args.nameFilter, imageList)
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