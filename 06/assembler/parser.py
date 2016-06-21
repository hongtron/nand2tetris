#!/usr/bin/env python
import string, command

class Parser:
    def __init__(self, input_file, skip_pseudos):
        self.input_file = open(input_file, 'r')
        self.working_input = self.clean(self.input_file, skip_pseudos)
        self.cur_cmd = ''
    
    # remove comments and whitespace, and store input file as list of lines (self.working_input)
    def clean(self, input_file, skip_pseudos):
        working_input = []
        for line in input_file:
            for whitespace in string.whitespace: # loop through whitespace characters
                if whitespace == '\n': # don't remove newlines
                    pass
                else: # do remove all other whitespace characters
                    segments = line.split(whitespace)
                    line = ''.join(segments)
            if len(line.split('//')) > 1: # check for comment
                line = line.split('//', 1)[0] # if found, ignore everything after the first instance of '//'
                line += '\n' # restore newline that got chopped off
            if (line != '\n'): # ignore empty lines
                if skip_pseudos & (line[0] == '('):
                    pass # ignore pseudocommands if skip_pseudos
                else:
                    working_input.append(line);
        return working_input

    def has_more_commands(self):
        if len(self.working_input) > 0:
            return True
        else:
            return False

    def advance(self):
        self.cur_cmd = command.Command(self.working_input.pop(0)[:-1]) # ignore the newline at the end

    def command_type(self):
        return self.cur_cmd.c_type

    def symbol(self):
        return self.cur_cmd.symbol

    def dest(self):
        return self.cur_cmd.dest

    def comp(self):
        return self.cur_cmd.comp

    def jump(self):
        return self.cur_cmd.jump
