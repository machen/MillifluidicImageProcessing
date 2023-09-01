# Code to process images. Should be run from command line targetting a specific folder

import sys
import os
import re
from argparse import ArgumentParser
import numpy as np
import skimage as sk
from skimage.io import imread
from skimage.filters import threshold_isodata
from skimage.measure import label, regionprops_table
from skimage.morphology import disk, white_tophat
import matplotlib.pyplot as plt


def generateDiffIm(index, image, diffImage, initImage, threshold=1) -> np.ndarray:
    """ Adapted from code by Marcel Moura @ PoreLab - UiO (09/2022) code for fluid invasion image processing.

    Parameters
    ---------
    index: Index of the image you want to do the comparison on, used for color
    image: Image to do next comparison on
    diffImage: Current diffImage
    initImage: Initial image to compare against
    threshold: Optional int that specifies the threshold for considering an image different from the initial. Deafult of 1 presumes binary images.

    Returns
    ------
    diffIm: Updated diffImage
    """
    # Area where the image has changed from initial
    diff = (image-initImage) >= threshold
    # Area of image that has not yet changed
    diffImDelta = diffImage == 0 # Demarcate areas that have not yet changed
    # Element-wise AND of the above set to index of the image
    diffImage[np.logical_and(diff, diffImDelta)] = index
    return diffImage


def setImageCrop(baseImage) -> tuple[int, int, int, int]:
    # TODO: Should use some other criteria to crop the image, such as user input on a test figure
    x1 = 0
    y1 = 0
    x2 = baseImage.shape[1] # np.arrays are [row,col]
    y2 = baseImage.shape[0]
    return x1, y1, x2, y2


def createImageList(folderName, fileExt,
                    nameFilter) -> dict:
    """ Scan through image names in folderName with file
    extension fileExt and matching pattern nameFilter

    Parameters
    ---------
    folderName: Folder to scan
    fileExt: File extenstion for the files to include
    nameFilter: regex expression for filtering out which files to use

    Returns
    --------
    imageList: Dict of images matching the filter, indexed by the group specified in nameFilter
    """
    imageList = {}
    filePat = re.compile(nameFilter)
    for item in os.listdir(folderName):
        # Filter on filePat and extension
        # TODO: Should handle passing no nameFilter and cases with multiple matching indices
        match = re.match(filePat, item)
        if match and item.endswith(fileExt):
            index = match.group(1)
            imageList[int(index)] = item
    return imageList


def imageProcess(image):
    # TODO: Should decide on correct thresholding algorithm
    # Images may need multiple thresholds to delineate surface vs bottom
    # TODO: May also want to do image registration to detect if the image has moved at all
    thresh = threshold_isodata(image)
    mask = image > thresh
    # label_img = label(mask)
    # footprint = disk(10)
    # res = white_tophat(mask, footprint)
    # fullProps = sk.measure.regionprops(label_img, intensity_image=image)
    # fig, ax = plt.subplots()
    # # Plotting to show the image,
    # # TODO: Should be a flag to plot
    # # TODO: What do we do with the masked images?
    # # TODO: Need to filter out small objects, consider sk.morphology.white_tophat()
    # ax.imshow(res, cmap='gray')
    # fig2, ax2 = plt.subplots()
    # ax2.imshow(image-res > thresh, cmap='gray')
    # # for props in fullProps:
    # #     equivCircRad = np.sqrt(props.area)/np.pi
    # #     y0, x0 = props.centroid
    # #     circle = plt.Circle((x0, y0), equivCircRad, color='r',alpha=0.3)
    # #     ax.add_patch(circle)
    # plt.show()
    maskOut = np.array(mask, dtype='uint16')
    return maskOut


def main(args) -> int:
    imageList = createImageList(args.folderName, args.fileExt, args.nameFilter)
    initImage = imageProcess(imread(args.folderName+os.sep+imageList[1],
                                    as_gray=True))
    diffImage = np.zeros(initImage.shape)
    for index in sorted(imageList.keys()):
        imFile = imageList[index]
        print(imFile)
        # TODO: This is really hacky and I need a better way to specify the first image and image sequence
        image = imread(args.folderName+os.sep+imFile, as_gray=True)
        threshIm = imageProcess(image)
        # images[imFile] =
        diffImage = generateDiffIm(index, threshIm, diffImage, initImage)
    fig, ax = plt.subplots()
    plt.imshow(diffImage, cmap='turbo')
    plt.colorbar()
    plt.show()
    return 0


if __name__ == '__main__':
    parser = ArgumentParser(prog='millifluidic',
                            description='Greyscale image processing for millifluidic images',
                            epilog='Currently in development')
    parser.add_argument('folderName')
    parser.add_argument('fileExt')
    # TODO: You should either specify a name filter which has a regex group that the index is drawn from, and needs to specify the index or a file which gives the indices explicitly
    parser.add_argument('nameFilter')
    parser.add_argument('-c', '--cropImage', nargs=4)
    args = parser.parse_args()
    sys.exit(main(args))