#!/usr/bin/env python
import string

class Command:
    def __init__(self, command):
        if command[0] == '@':
            self.c_type = 'A_COMMAND'
            try:
                self.symbol = int(command[1:])  # if integer symbol, store as int
            except ValueError:
                self.symbol = command[1:]  # otherwise, store as string to be looked up in symbol table later
            self.dest = None
            self.jump = None
            self.comp = None
        elif command[0] == '(':
            self.c_type = 'L_COMMAND'
            self.symbol = command[1:-1]
            self.dest = None
            self.jump = None
            self.comp = None
        else:
            self.c_type = 'C_COMMAND'
            eq_index = string.find(command, '=')
            sc_index = string.find(command, ';')
            self.symbol = None
            if eq_index != -1:  # if dest is not empty
                self.dest = command[0:eq_index]
            else:
                self.dest = "nowhere"
            if sc_index != -1:  # if jump is not empty
                self.comp = command[eq_index+1:sc_index]
                self.jump = command[sc_index+1:]
            else:
                self.comp = command[eq_index+1:]
                self.jump = "nowhere"
