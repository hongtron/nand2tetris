#!/usr/bin/env python


# emits VM commands into a file using the VM command syntax
class VMWriter:
    def __init__(self, output_file):
        self.output_file = open(output_file, 'w+')

    def write_command(self, command, arg1='', arg2=''):
        self.output_file.write(command + ' ' + str(arg1) + ' ' + str(arg2) + '\n')

    def write_push(self, segment, index):
        self.write_command('push', segment, index)

    def write_pop(self, segment, index):
        self.write_command('pop', segment, index)

    def write_arithmetic(self, command):
        self.write_command(command)

    def write_label(self, label):
        self.write_command('label', label)

    def write_goto(self, label):
        self.write_command('goto', label)

    def write_if(self, label):
        self.write_command('if-goto', label)

    def write_call(self, name, n_args):
        self.write_command('call', name, n_args)

    def write_function(self, name, n_locals):
        self.write_command('function', name, n_locals)

    def write_return(self):
        self.write_command('return')

    def close(self):
        self.output_file.close()
