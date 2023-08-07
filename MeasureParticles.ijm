// Perform image analysis to determine size of main pillar. Should save the resulting mask so you can compare
// Requires grayscale files which are produced by the ConvertRGBNefToTif.ijm script
#@ File (label = "Input directory", style = "directory") inputFolder
#@ File (label = "Output directory", style = "directory") outputFolder
#@ String (label = "File suffix", value = ".tif") suffix
#@ int (label = "Threshold Min") tMin
#@ int (label = "Threshold Max") tMax
#@ float (label = "Min particle size") pMin
#@ boolean (label = "Crop based on current selection") crop


//run("Close All");
sweepFolder(inputFolder);

print("Output complete");

function sweepFolder(inputFolder) {
	list = getFileList(inputFolder);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(inputFolder + File.separator + list[i])){
		sweepFolder(inputFolder + File.separator + list[i]);
		}
	if(endsWith(list[i], suffix)) {
		measureFile(inputFolder, outputFolder, list[i], tMin, tMax, pMin);
		}	
	}
}

function measureFile(inputFolder, outputFolder, file, tMin, tMax, pMin){
	open(inputFolder+File.separator+file);
	if (crop){
		run("Restore Selection");
		run("Crop");
	}
	setThreshold(tMin, tMax);
	run("Convert to Mask");
	run("Analyze Particles...", "size="+pMin+"-Infinity show=Outlines display include");
	saveAs("Tiff",outputFolder+File.separator+replace(file,".tif","_particle.tif"));
	close("*");
}
