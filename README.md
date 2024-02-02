# Millifluidic Image Processing
A collection of codes used for analyzing experimental images generated from the UMN Kang Research Group Millifluidic setup. Main code, Millifluidic.py, takes a folder of aligned images and does image analysis to a) Produce a color-coded map of a changing interface (here, receding mineral) in time, and b) Calculate total areas. PIVdata.py is used in conjunction with Dantec Dynamics stereo PIV data sets to produce files that can be visualized via Paraview

# Dependencies
millifluidic.yml proscribes the environment and necessary packages using an Anaconda Python installation. Code originally developed on Windows 11, but *should* be functional on other OS's.
