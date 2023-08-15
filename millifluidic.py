# Code to process images. Should be run from command line targetting a specific folder

import sys
import os
import re
from argparse import ArgumentParser
import numpy as np
import skimage as sk
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops_table
import matplotlib.pyplot as plt


def generateDiffIm(images, initImageKey=0, threshold=1) -> np.ndarray:
    """ Adapted from code by Marcel Moura @ PoreLab - UiO (09/2022) code for fluid invasion image processing.

    Parameters
    ---------
    images: Dict with keys of index and an associated thresholded image (np.array) of the same size and shape.
    initImageKey: Index of the image which should be considered intial. Default value is 0.
    threshold: Optional int that specifies the threshold for considering an image different from the initial. Deafult of 1 presumes binary images.

    Returns
    ------
    diffIm: numpy array where the values indicate the image index at which there first a difference
    """
    initImage = images[initImageKey]
    diffIm = np.zeros(initImage.shape())
    for index, image in images.index():
        # Area where the image has changed from initial
        diff = (image-initImage) >= threshold
        # Area of image that has not yet changed
        diffImDelta = diffIm == 0
        # Element-wise AND of the above set to index of the image
        diffIm[np.logical_and(diff, diffImDelta)] = index
    return diffIm


def setImageCrop(baseImage) -> tuple(int,int,int,int):
    # TODO: Should use some other criteria to crop the image, such as user input on a test figure
    x1 = 0
    y1 = 0
    x2 = baseImage.shape[1] # np.arrays are [row,col]
    y2 = baseImage.shape[0]
    return x1, y1, x2, y2


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
    # TODO: May also want to do image registration to detect if the image has moved at all
    thresh = threshold_otsu(image)
    mask = image > thresh
    label_img = label(mask)
    footprint = sk.morphology.disk(3)
    res = sk.morphology.white_tophat(mask, footprint)
    fullProps = sk.measure.regionprops(label_img, intensity_image=image)
    fig, ax = plt.subplots()
    # Plotting to show the image,
    # TODO: Should be a flag to plot
    # TODO: What do we do with the masked images?
    # TODO: Need to filter out small objects, consider sk.morphology.white_tophat()
    ax.imshow(image, cmap=plt.cm.gray)
    fig2, ax2 = plt.subplots()
    ax2.imshow(image-res, cmap='gray')
    # for props in fullProps:
    #     equivCircRad = np.sqrt(props.area)/np.pi
    #     y0, x0 = props.centroid
    #     circle = plt.Circle((x0, y0), equivCircRad, color='r',alpha=0.3)
    #     ax.add_patch(circle)
    plt.show()
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