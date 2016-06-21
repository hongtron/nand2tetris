#!/usr/bin/env python
import string, command

class Parser:
    # constructor: create a new parser object; each new file should use a new parser
    ## parameters: input_file - the file currently being parsed
    def __init__(self, input_file):
        self.input_file = open(input_file, 'r')
        self.working_input = self.clean(self.input_file)
        self.cur_cmd = ''
    
    # remove comments and whitespace, and store input file as list of lines (self.working_input)
    # parameters: input_file - the file currently being parsed
    def clean(self, input_file):
        working_input = []
        for line in input_file:
            for whitespace in string.whitespace: # loop through whitespace characters
                if (whitespace == '\n') or (whitespace == ' '): # don't remove newlines or spaces
                    pass
                else: # do remove all other whitespace characters
                    segments = line.split(whitespace)
                    line = ''.join(segments)
            if len(line.split('//')) > 1: # check for comment
                line = line.split('//', 1)[0] # if found, ignore everything after the first instance of '//'
                line += '\n' # restore newline that got chopped off
            if (line != '\n'): # ignore empty lines
                working_input.append(line);
        return working_input

    # returns True if there are more commands to parse, False o/w
    def has_more_commands(self):
        if len(self.working_input) > 0:
            return True
        else:
            return False

    # move on to the next command to be parsed
    def advance(self):
        self.cur_cmd = command.Command(self.working_input.pop(0)[:-1]) # ignore the newline at the end

    # return the type of the command currently being parsed
    def command_type(self):
        return self.cur_cmd.c_type

    # return arg1 of the command currently being parsed
    def arg1(self):
        return self.cur_cmd.arg1

    # return arg2 of the command currently being parsed
    def arg2(self):
        return self.cur_cmd.arg2