#!/usr/bin/env python

import jack_tokenizer
import symbol_table
import compilation_engine
import vm_writer
import sys
import os


# creates a .vm output for each input .jack file
class JackCompiler():
    # constructor: determine appropriate output destination
    # parameters: input_file - location of .jack file(s) to be tokenized
    def __init__(self):
        pass

    def compile(self, input_file):
        tokenizer = jack_tokenizer.JackTokenizer(input_file)
        table = symbol_table.SymbolTable()
        vm_out = input_file.replace('.jack', '.vm')
        writer = vm_writer.VMWriter(vm_out)
        engine = compilation_engine.CompilationEngine(tokenizer, table, writer)
        engine.compile_class()


def main():
    filein = sys.argv[1]
    jacomp = JackCompiler()
    if os.path.isdir(filein):  # if directory, loop through files
        # remove trailing slash for directories if present
        if filein[-1:] == '/':
            filein = filein[:-1]
            for current_file in os.listdir(filein):
                if '.jack' in current_file:
                    current_file = os.path.join(filein, current_file)
                    jacomp.compile(current_file)
    else:
        if '.jack' in filein:
            jacomp.compile(filein)
        else:
            print 'Invalid input.'

main()
