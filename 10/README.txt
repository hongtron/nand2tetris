Function:
This program creates two outputs from a Jack file: a token list, and a semantic map.

Requirements:
Python 2.7

Running:
To run the program, first navigate to the project directory (/ali hong 10/) via the command line.
The syntax to run the program is as follows.

python compiler/jack_analyzer.py /path/to/input/file.jack

Or, if the input is a directory.

python compiler/jack_analyzer.py /path/to/input/directory/
(Trailing slash optional)

Input/Output:
The input should be a .jack file or a directory. If the input is a file, the output file will output two files, filenameT.xml and filename.xml.  If the input is a directory, these output files will be generated for each .jack file in the directory.