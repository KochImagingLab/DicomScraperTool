# DicomScraperTool
Tool for scraping folders of DICOM files 

The tool is designed to automatically and recursively move though an input directory, find groups of DICOM files within each folder, read one of the files, and then extract the dicom keys/tags requested in the input key list file and place them into a dataframe, which is output in the requested output CSV filename.   

To determine which keys and pre-defined tags can be listed, see the .pdf file in the repository, which has a list of those utilized by the pydicom library. 

A sample key list file is also included in the repository. 

Usage of the tool: 

python DicomScraperTool -p searchpath -k keyfile -o outputfile (use .csv as extension)
