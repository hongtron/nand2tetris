#!/usr/bin/env python

import jack_tokenizer
import compilation_engine
import sys
import os


class JackAnalyzer():
    # constructor: determine appropriate output destination
    # parameters: input_file - location of .jack file(s) to be tokenized
    def __init__(self):
        pass

    def analyze(self, input_file):
        tokenizer = jack_tokenizer.JackTokenizer(input_file)
        output_file = input_file.replace('.jack', '.xml')
        engine = compilation_engine.CompilationEngine(tokenizer, output_file)
        engine.compile_class()


def main():
    filein = sys.argv[1]
    jan = JackAnalyzer()
    if os.path.isdir(filein):  # if directory, loop through files
        # remove trailing slash for directories if present
        if filein[-1:] == '/':
            filein = filein[:-1]
            for current_file in os.listdir(filein):
                if '.jack' in current_file:
                    current_file = os.path.join(filein, current_file)
                    jan.analyze(current_file)
    else:
        if '.jack' in filein:
            jan.analyze(filein)
        else:
            print 'Invalid input.'

main()
