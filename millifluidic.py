# Code to process images. Should be run from command line targetting a specific folder

import sys
import os
import re
from argparse import ArgumentParser
import numpy as np
from skimage.io import imread
from skimage.filters import threshold_isodata
from skimage.transform import estimate_transform, warp
from skimage.measure import label, regionprops
import matplotlib.pyplot as plt
from skimage import feature
import pandas as pd
from skimage.feature import match_descriptors, ORB


def generateDiffIm(index, image, diffImage, initImage, threshold=50) -> np.ndarray:
    """ Adapted from code by Marcel Moura @ PoreLab - UiO (09/2022) code for fluid invasion image processing.

    Parameters
    ---------
    index: Index of the image you want to do the comparison on, used for color
    image: Image to do next comparison on, should be a binary image
    diffImage: Current diffImage
    initImage: Initial image to compare against
    threshold: Optional int that specifies the threshold for considering an image different from the initial.
               Only used if the arrays are not boolean

    Returns
    ------
    diffIm: Updated diffImage
    """
    # Area where the image has changed from initial
    if image.dtype == np.dtype('bool'):
        diff = np.logical_xor(image, initImage)
    else:
        diff = (image-initImage) >= threshold
    # Area of image that has not yet changed
    diffImDelta = diffImage == 0  # Demarcate areas that have not yet changed
    # Element-wise AND of the above set to index of the image
    diffImage[np.logical_and(diff, diffImDelta)] = index
    return diffImage


def setImageCrop(baseImage) -> tuple[int, int, int, int]:
    # TODO: Should use some other criteria to crop the image, such as user input on a test figure
    x1 = 0
    y1 = 0
    x2 = baseImage.shape[1]  # np.arrays are [row,col]
    y2 = baseImage.shape[0]
    return x1, y1, x2, y2


def cropImage(image, coords):
    x1 = coords[0]
    y1 = coords[2]
    x2 = coords[1]
    y2 = coords[3]
    # Arrays are addressed [row, column]
    return image[y1:y2, x1:x2]


def parseInputFile(inputFile) -> pd.DataFrame:
    """" Alternative function for generating the image list,
    should give index and filename, and should be sorted to chronological order.


    """
    data = pd.read_csv(inputFile, header=0, index_col='index')
    data.sort_values(by='elapsedTime', inplace=True)
    imageList = data.loc[data.use, :]
    return imageList


def imageAlignment(image1, image2):
    """Function meant for aligning images DO NOT USE
    Images should be aligned using FIJI (or already aligned)"""
    raise NotImplementedError("Image alignment is too expensive to run on a per-batch basis. Pre-align images.")
    descriptor_extractor = ORB(n_keypoints=20)
    # Generate Keypoints of first image
    descriptor_extractor.detect_and_extract(image1)
    keyPoint1 = descriptor_extractor.keypoints
    descriptors1 = descriptor_extractor.descriptors
    # Generate Keypoints of second image
    descriptor_extractor.detect_and_extract(image2)
    keyPoint2 = descriptor_extractor.keypoints
    descriptors2 = descriptor_extractor.descriptors

    matches = match_descriptors(descriptors1, descriptors2, max_ratio=0.8, cross_check=True)
    src = []
    dst = []
    for pair in matches:
        srcPoint = keyPoint1[pair[0]]
        src.append(srcPoint)
        dstPoint = keyPoint2[pair[1]]
        dst.append(dstPoint)
    src = np.array(src)
    dst = np.array(dst)
    transfEst = estimate_transform('similarity', src, dst)
    imageOut = warp(image2, transfEst.inverse)
    return imageOut


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


def createImageMask(image) -> np.ndarray:
    # TODO: Should decide on correct thresholding algorithm
    # Images may need multiple thresholds to delineate surface vs bottom
    # DONE: May also want to do image registration to detect if the image has moved at all
    thresh = threshold_isodata(image)
    mask = image > thresh
    # Also need to filter label_img to give back only the selected regions
    return mask


def calcImageArea(mask, image, areaThresh=1000) -> float:
    label_img = label(mask)
    # footprint = disk(10)
    # res = white_tophat(mask, footprint)
    fullProps = regionprops(label_img, intensity_image=image)
    selectProps = []
    totalArea = 0
    for region in fullProps:
        if region.area > areaThresh:
            selectProps.append(region)
            totalArea += region.area
    return totalArea


def main(args) -> int:
    plt.rcParams['svg.fonttype'] = 'none'  # Need to output fonts correctly
    title = ''  # Bind empty string to title just in case
    if args.inputFile:
        imageList = parseInputFile(args.folderName+os.sep+args.inputFile)
        title = 'Color by elapsed time'
    elif args.manualList:
        fileExt = args.manualList[1]
        nameFilter = args.manualList[0]
        imageList = createImageList(args.folderName,
                                    fileExt, nameFilter)
        title = 'Color by index'
    firstImage = imageList.loc[imageList.index.min(), 'imageFile']
    initIm = imread(args.folderName+os.sep+firstImage, as_gray=True)
    if args.cropImage:
        initIm = cropImage(initIm, args.cropImage)
    # We only care about the initial image to populate what the initial shape should be
    initialMaskImage = createImageMask(initIm)
    diffImage = np.zeros(initialMaskImage.shape)
    areas = []
    times = []
    for index in imageList.index:
        if args.inputFile:
            # Color by actual elapsed time if using input file
            imageTime = imageList.loc[index, 'elapsedTime']
        else:
            # Use index of image as proxy for time otherwise
            imageTime = index
        times.append(imageTime)
        imFile = imageList.loc[index, 'imageFile']
        print(imFile)
        # DONE: This is really hacky, need to better specify the first image
        # First image from input file or smallest index
        image = imread(args.folderName+os.sep+imFile, as_gray=True)
        if args.cropImage:
            image = cropImage(image, args.cropImage)
        imageMask = createImageMask(image)
        # threshImage = image*imageMask
        if args.thresholdArea:
            imageArea = calcImageArea(imageMask, image, args.thresholdArea)
        else:
            imageArea = calcImageArea(imageMask, image)
        areas.append(imageArea)
        diffImage = generateDiffIm(imageTime, imageMask,
                                   diffImage, initialMaskImage)
        # Save the mask images. Slow.p
        if args.saveMask:
            plt.imshow(imageMask)
            maskFolder = args.folderName+os.sep+'MaskImages'
            try:
                os.mkdir(maskFolder)
            except FileExistsError:
                pass
            plt.savefig(maskFolder+os.sep+imFile)

    fig, ax = plt.subplots()
    # Set max and min of plot
    if args.rangeMin:
        minPlotValue = args.rangeMin
    else:
        minPlotValue = 0
    if args.rangeMax:
        maxPlotValue = args.rangeMax
    else:
        maxPlotValue = float(np.max(diffImage, axis=None))
    plt.imshow(diffImage, cmap='turbo', vmin=minPlotValue, vmax=maxPlotValue)
    plt.colorbar(label=title)
    fig3, ax3 = plt.subplots()
    plt.imshow(diffImage*initialMaskImage, cmap='turbo', vmin=minPlotValue, vmax=maxPlotValue)
    plt.colorbar(label=title+'Diff image masked by first image')
    fig2, ax2 = plt.subplots()
    plt.plot(times, areas)
    plt.show()
    if args.saveName:
        saveName = args.saveName
    elif args.inputFile:
        saveName = args.inputFile
    else:
        saveName = 'Processed'
    saveLocation = args.folderName+os.sep+saveName
    fig.savefig(saveLocation+' Difference Image.svg', dpi=300)
    fig2.savefig(saveLocation+' Areas.svg', dpi=300)
    fig3.savefig(saveLocation+'Initial Masked Difference Image.svg', dpi=300)
    np.save(saveLocation+' diffImage.npy', diffImage)
    np.save(saveLocation+' elapsedTimes.npy', times)
    np.save(saveLocation+' totalAreas.npy', areas)
    np.save(saveLocation+' initialMaskImage.npy', initialMaskImage)
    return 0


if __name__ == '__main__':
    parser = ArgumentParser(prog='millifluidic',
                            description='Greyscale image processing for millifluidic images',
                            epilog='Currently in development')
    parser.add_argument('folderName',
                        help="Folder location containing images and image list, if using")
    parser.add_argument('-f', '--inputFile', type=str,
                        help="csv containing the list of files, see template")
    parser.add_argument('-l', '--manualList', nargs=2,
                        default=['.*', '.tif'],
                        help="""2 args, First is a regex string matching the file names, Second is file extension.
                                Used if no other data for the list of images is given.""")
    parser.add_argument('-c', '--cropImage',
                        nargs=4, type=int,
                        help="Use np matrix format with origin in top left corner, giving coords x1 x2 y1 y2")
    parser.add_argument('-t', '--thresholdArea', type=int,
                        help="Minimum area for identifying thresholded areas. Use to filter out small objects.")
    parser.add_argument('-m', '--saveMask')
    parser.add_argument('-n', '--saveName', type=str)
    parser.add_argument('--rangeMax', type=float)
    parser.add_argument('--rangeMin', type=float)
    args = parser.parse_args()
    sys.exit(main(args))
