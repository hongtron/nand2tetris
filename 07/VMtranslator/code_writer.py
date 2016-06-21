#!/usr/bin/env python

class CodeWriter():
    # constructor: used to translate from intermediate code to Hack assembly
    ## parameters: output_file - .asm file where assembly instructions will be output
    def __init__(self, output_file):
        self.output_file = open(output_file, "w+")
        self.file_name = ''
        self.label_counter = -1
        self.symbols = {
            'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT', 'pointer':'3', 'temp':'5'
        }
    
    # update the file name (used for prefixing) when a new file is passed in
    ## parameters: file_name - the name of the file being translated
    def set_file_name(self, file_name):
        self.file_name = file_name

    # write arithmetic functions
    ## parameters: command - the command being translated
    def write_arithmetic(self, command):
        if command == "add" : self.binary_op('M=D+M\n')
        elif command == "sub" : self.binary_op('M=M-D\n')
        elif command == "and" : self.binary_op('M=D&M\n')
        elif command == "or" : self.binary_op('M=D|M\n')
        elif command == "neg" : self.unary_op('M=-M\n')
        elif command == "not" : self.unary_op('M=!M\n')
        elif command == "gt" : self.comp_op("JGT")
        elif command == "lt" : self.comp_op("JLT")
        elif command == "eq" : self.comp_op("JEQ")

    # write push/pop behavior
    ## parameters: command - the command being translated
    def write_push_pop(self, command, segment, index):
        if command == "C_PUSH":
            if segment == "constant":
                self.output_file.write("@" + index + "\n")
                self.output_file.write("D=A\n")
                self.push_d()

            else:
                self.compute_addr(segment, index)
                self.output_file.write("D=M\n")
                self.push_d()
        else: # C_POP
            self.compute_addr(segment, index)
            self.output_file.write("D=A\n")
            self.output_file.write("@R13\n")
            self.output_file.write("M=D\n") # store computed address in R13
            self.output_file.write("@SP\n")
            self.output_file.write("AM=M-1\n")
            self.output_file.write("D=M\n") # store popped value in D
            self.output_file.write("@R13\n")
            self.output_file.write("A=M\n")
            self.output_file.write("M=D\n")

    # close the output file
    def close(self):
        self.output_file.close()

    # helper function for writing binary operations; stores the second operand in D, and loads the address of the first operand into A
    ## parameters: op_line - contains the operation-specific logic
    def binary_op(self, op_line):
        self.output_file.write("@SP\n")
        self.output_file.write("AM=M-1\n")
        self.output_file.write("D=M\n")
        self.output_file.write("A=A-1\n")
        self.output_file.write(op_line)

    # helper function for writing unary operations; loads the address of the operand into A
    ## parameters: op_line - contains the operation-specific logic
    def unary_op(self, op_line):
        self.output_file.write("@SP\n")
        self.output_file.write("A=M-1\n")
        self.output_file.write(op_line)

    # helper function for writing comparison operations
    ## parameters: comp_type - contains the comparison-specific logic
    def comp_op(self, comp_type):
        self.label_counter += 1
        self.binary_op("D=M-D\n") # perform subtraction, but store result in D rather than M
        # labels should be prefixed with filename to avoid collisions across files, and suffixed with counter to avoid collisions within files
        self.output_file.write("@" + self.file_name + ".COMP" + str(self.label_counter) + "\n")
        self.output_file.write("D;" + comp_type + "\n")
        self.output_file.write("@SP\n")
        self.output_file.write("A=M-1\n")
        self.output_file.write("M=0\n") # false
        self.output_file.write("@" + self.file_name + ".END" + str(self.label_counter) + "\n")
        self.output_file.write("0;JMP\n")
        self.output_file.write("(" + self.file_name + ".COMP" + str(self.label_counter) + ")\n")
        self.output_file.write("@SP\n")
        self.output_file.write("A=M-1\n")
        self.output_file.write("M=-1\n") # true
        self.output_file.write("(" + self.file_name + ".END" + str(self.label_counter) + ")\n")

    # write code to push value in D to stack
    def push_d(self):
        self.output_file.write("@SP\n")
        self.output_file.write("A=M\n")
        self.output_file.write("M=D\n")
        self.output_file.write("@SP\n")
        self.output_file.write("M=M+1\n")

    # compute address given segment and offset, and store it in A
    ## parameters: seg - memory segment; offset - index in segment
    def compute_addr(self, seg, offset):
        if seg == "static":
            self.output_file.write("@" + self.file_name + "." + offset + "\n")
        else:
            self.output_file.write("@" + offset + "\n")
            self.output_file.write("D=A\n")
            self.output_file.write("@" + self.symbols[seg] + "\n") # translate to assembly-level symbols
            if seg not in ('pointer', 'temp'):
                self.output_file.write("A=M\n") # if pointer or temp, use the literal value 3 or 5
            self.output_file.write("A=A+D\n")
        