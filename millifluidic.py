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
from skimage import feature
import pandas as pd


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


def cropImage(image, coords):
    x1 = coords[0]
    y1 = coords[1]
    x2 = coords[2]
    y2 = coords[3]
    return image[x1:x2, y1:y2]


def parseInputFile(inputFile) -> pd.DataFrame:
    """" Alternative function for generating the image list,
    should give index and filename, and should be sorted to chronological order.


    """
    data = pd.read_csv(inputFile, header=0, index_col='index')
    data.sort_values(by='elapsedTime', inplace=True)
    imageList = data.loc[data.use == True, :]
    return imageList


def createImageList(folderName, fileExt,
                    nameFilter) -> pd.DataFrame:
    """ Scan through image names in folderName with file
    extension fileExt and matching pattern nameFilter.

    Requires a name filter which specifies at least one group
    which is used to match the index

    Parameters
    ---------
    folderName: Folder to scan
    fileExt: File extenstion for the files to include
    nameFilter: regex expression for filtering out which files to use, must include a group for what the file index is

    Returns
    --------
    imageList: DataFrame of images matching the filter, index is the number
    """
    imageList = {}
    filePat = re.compile(nameFilter)
    if filePat.groups < 1:
        raise ValueError('nameFilter must include at least one group specifying an index, or use an input file (-f)')
    for item in os.listdir(folderName):
        # Filter on filePat and extension
        # TODO: Should handle passing no nameFilter and cases with multiple matching indices
        match = re.match(filePat, item)
        if match and item.endswith(fileExt):
            index = match.group(1)
            imageList[int(index)] = item
    imageList = pd.DataFrame.from_dict(imageList, orient='index',
                                       columns=['imageFile'])
    return imageList


def detectAndPlotEdges(image, sigma):
    """ Function used to test out edge finding on images.
    Didn't work well due to high noise in our images
    """
    edge = feature.canny(image, sigma=sigma)
    print(edge)
    f, ax = plt.subplots(nrows=1, ncols=2)
    ax[0].imshow(image, cmap='gray')
    ax[1].imshow(edge, cmap='turbo')
    ax[1].set_title("Edge plot")
    return edge


def imageProcess(image, plot=False, areaThresh = 500000):
    # TODO: Should decide on correct thresholding algorithm
    # Images may need multiple thresholds to delineate surface vs bottom
    # TODO: May also want to do image registration to detect if the image has moved at all
    thresh = threshold_isodata(image)
    mask = image > thresh
    label_img = label(mask)
    # footprint = disk(10)
    # res = white_tophat(mask, footprint)
    fullProps = sk.measure.regionprops(label_img, intensity_image=image)
    selectProps = []
    for region in fullProps:
        if region.area > areaThresh:
            selectProps.append(region)
    # Also need to filter label_img to give back only the selected regions
    # Plotting to show the image,
    # DONE: Should be a flag to plot
    # TODO: What do we do with the masked images?
    # TODO: Need to filter out small objects, consider sk.morphology.white_tophat()
    if plot:
        fig, ax = plt.subplots(1, 2)
        ax[0].imshow(image, cmap='gray')
        ax[0].set_title('Original Image')
        cb = ax[1].imshow(label_img, cmap='turbo')
        ax[1].set_title('Label image')
        fig.colorbar(cb)
    # for props in fullProps:
    #     equivCircRad = np.sqrt(props.area)/np.pi
    #     y0, x0 = props.centroid
    #     circle = plt.Circle((x0, y0), equivCircRad, color='r',alpha=0.3)
    #     ax.add_patch(circle)
    maskOut = np.array(mask, dtype='uint16')
    return maskOut


def main(args) -> int:
    if args.inputFile:
        imageList = parseInputFile(args.inputFile)
        title = 'Color by elapsed time'
    else:
        imageList = createImageList(args.folderName, args.fileExt, args.nameFilter)
        title = 'Color by index'
    firstImage = imageList.loc[imageList.index.min(), 'imageFile']
    initImage = imageProcess(imread(args.folderName+os.sep+firstImage,
                                    as_gray=True))
    if args.cropImage:
        initImage = cropImage(initImage, args.cropImage)
    diffImage = np.zeros(initImage.shape)
    for index in imageList.index:
        imFile = imageList.loc[index, 'imageFile']
        print(imFile)
        # DONE: This is really hacky, need to better specify the first image
        # First image from input file or smallest index
        image = imread(args.folderName+os.sep+imFile, as_gray=True)
        if args.cropImage:
            image = cropImage(image, args.cropImage)
        threshIm = imageProcess(image, False)
        # images[imFile] =
        if args.inputFile:
            # Color by actual elapsed time if using input file
            diffImage = generateDiffIm(imageList.loc[index, 'elapsedTime'],
                                       threshIm, diffImage, initImage)
        else:
            # Use index of image as proxy for time otherwise
            diffImage = generateDiffIm(index, threshIm, diffImage, initImage)
    fig, ax = plt.subplots()
    plt.imshow(diffImage, cmap='turbo')
    plt.colorbar(label=title)
    plt.show()
    return 0


if __name__ == '__main__':
    parser = ArgumentParser(prog='millifluidic',
                            description='Greyscale image processing for millifluidic images',
                            epilog='Currently in development')
    parser.add_argument('folderName')
    parser.add_argument('fileExt')
    parser.add_argument('nameFilter')
    parser.add_argument('-c', '--cropImage', nargs=4, type=int)
    parser.add_argument('-f', '--inputFile', type=str)
    args = parser.parse_args()
    sys.exit(main(args))