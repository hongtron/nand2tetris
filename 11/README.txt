Function:
This program is a compiler for the Jack language.

Requirements:
Python 2.7

Running:
To run the program, first navigate to the project directory (/ali hong 11/) via the command line.
The syntax to run the program is as follows.

python compiler/jack_compiler.py /path/to/input/file.jack

Or, if the input is a directory.

python compiler/jack_compiler.py /path/to/input/directory/
(Trailing slash optional)

Input/Output:
The input should be a .jack file or a directory. If the input is a file, the output file will output one .vm file with the same file name as the .jack input, and one .xml output containing the tokenized Jack program.  If the input is a directory, one .vm file and one .xml file will be created for each .jack file in the directory.