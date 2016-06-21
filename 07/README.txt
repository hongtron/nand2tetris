Function:
This program is designed to translate from intermediate code into Hack assembly language.

Requirements:
Python 2.7

Running:
To run the program, first navigate to the project directory (/07/) via the command line.
The syntax to run the program is as follows.

python VMtranslator/vm_translator.py /path/to/input/file.vm

Or, if the input is a directory.

python VMtranslator/vm_translator.py /path/to/input/directory/

Input/Output:
The input should be a .vm file or a directory. If the input is a file, the output file will use the same filename with the extension .asm, and will be placed in the same directory as the input file.  If the input is a directory, the output file will use the name of the directory with the extension .asm, and will be placed at the same level as the directory.