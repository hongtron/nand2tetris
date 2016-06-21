#!/usr/bin/env python

import parser, code_writer, sys, os

class VMTranslator():
    # constructor: determine appropriate output destination
    ## parameters: input_file - location of .vm files to be translated (file or dir)
    def __init__(self, input_file):
        if os.path.isdir(input_file):
            output_file = input_file[:-1] + '.asm' # if input is directory, place output file on same level as input
        else:
            output_file = (input_file.rsplit('.vm', 1))[0] + '.asm'
        self.cw = code_writer.CodeWriter(output_file)

    # translate each new file to Hack assembly
    ## parameters: current_file - the file that schould be translated next
    def convert_file(self, current_file):
        file_name = (os.path.basename(current_file)).split('.')[0] # get the file name, excluding path and extension
        self.cw.set_file_name(os.path.basename(file_name))
        prs = parser.Parser(current_file)
        while prs.has_more_commands():
            prs.advance()
            if prs.command_type() == 'C_ARITHMETIC':
                self.cw.write_arithmetic(prs.arg1())
            elif prs.command_type() in ('C_PUSH', 'C_POP'):
                self.cw.write_push_pop(prs.command_type(), prs.arg1(), prs.arg2())

def main():
    filein = sys.argv[1]
    vmt = VMTranslator(filein)
    if os.path.isdir(filein): # if directory, loop through files
        for current_file in os.listdir(filein):
            vmt.convert_file(os.path.join(filein, current_file))
    else:
        vmt.convert_file(filein)
    vmt.cw.close()

main()
