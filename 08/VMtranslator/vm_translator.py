#!/usr/bin/env python

import parser, code_writer, sys, os

class VMTranslator():
    # constructor: determine appropriate output destination
    ## parameters: input_file - location of .vm files to be translated (file or dir)
    def __init__(self, input_file):
        if os.path.isdir(input_file):
            if input_file[-1:] == '/': # remove trailing slash for directories if present
                input_file = input_file[:-1]
            file_name = os.path.basename(input_file)
            output_file = file_name + '.asm' # get correct <filename>.asm
            output_file = os.path.join(input_file, output_file) # put <filename>.asm in correct directory
        else:
            output_file = (input_file.rsplit('.vm', 1))[0] + '.asm'
        self.cw = code_writer.CodeWriter(output_file)
        self.cw.write_init()

    # translate each new file to Hack assembly
    ## parameters: current_file - the file that schould be translated next
    def convert_file(self, current_file):
        file_name_pieces = (os.path.basename(current_file)).split('.')
        file_name = file_name_pieces[0] # get the file name, excluding path and extension
        ext = file_name_pieces[1]
        if ext == 'vm':
            self.cw.set_file_name(os.path.basename(file_name))
            prs = parser.Parser(current_file)
            while prs.has_more_commands():
                prs.advance()
                if prs.command_type() == 'C_ARITHMETIC':
                    self.cw.write_arithmetic(prs.arg1())
                elif prs.command_type() in ('C_PUSH', 'C_POP'):
                    self.cw.write_push_pop(prs.command_type(), prs.arg1(), prs.arg2())
                elif prs.command_type() == 'C_LABEL':
                    self.cw.write_label(prs.arg1())
                elif prs.command_type() == 'C_GOTO':
                    self.cw.write_goto(prs.arg1())
                elif prs.command_type() == 'C_IF':
                    self.cw.write_if(prs.arg1())
                elif prs.command_type() == 'C_FUNCTION':
                    self.cw.write_function(prs.arg1(), prs.arg2())
                elif prs.command_type() == 'C_RETURN':
                    self.cw.write_return()
                elif prs.command_type() == 'C_CALL':
                    self.cw.write_call(prs.arg1(), prs.arg2())

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
