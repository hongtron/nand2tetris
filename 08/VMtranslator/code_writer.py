#!/usr/bin/env python


class CodeWriter():
    # constructor: used to translate from intermediate code to Hack assembly
    # parameters: output_file - .asm file where assembly instructions
    # will be output
    def __init__(self, output_file):
        self.output_file = open(output_file, "w+")
        self.file_name = 'Sys'
        self.label_counter = -1
        self.symbols = {
            'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT',
            'pointer': '3', 'temp': '5'
        }

    # update the file name (used for prefixing) when a new file is passed in
    # parameters: file_name - the name of the file being translated
    def set_file_name(self, file_name):
        self.file_name = file_name

    # write arithmetic functions
    # parameters: command - the command being translated
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
                self.output_file.write("@" + str(index) + "\n")
                self.output_file.write("D=A\n")
                self.push_d()

            else:
                self.compute_addr(segment, index)
                self.output_file.write("D=M\n")
                self.push_d()
        else: # C_POP
            self.compute_addr(segment, index) # store correct address in A
            self.pop()

    # store top value in stack in memory address held in A
    def pop(self):
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
        # labels should be prefixed with filename to avoid collisions across
        # files, and suffixed with counter to avoid collisions within files
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

    ### PROJECT 8 FUNCTIONS ###
    def write_init(self):
        # bootstrap code
        self.output_file.write("@256\n")
        self.output_file.write("D=A\n")
        self.output_file.write("@SP\n")
        self.output_file.write("M=D\n") # SP=256
        self.write_call("Sys.init", 0)

    # write label
    ## parameters: label - name of label
    def write_label(self, label):
        self.output_file.write("(" + label + ")\n")

    # write goto behavior
    ## parameters: label - name of label to jump to
    def write_goto(self, label):
        self.output_file.write("@" + label + "\n")
        self.output_file.write("0;JMP\n")

    # write if-goto behavior
    ## parameters: label - name of label to jump to if value popped from stack is not 0
    def write_if(self, label):
        self.output_file.write("@SP\n")
        self.output_file.write("AM=M-1\n")
        self.output_file.write("D=M\n") # store popped value in D
        self.output_file.write("@" + label + "\n")
        self.output_file.write("D;JNE\n")

    # write call behavior
    ## parameters: function_name - name of function being called; num_args - number of args already pushed to stack
    def write_call(self, function_name, num_args):
        self.label_counter += 1
        new_label = self.file_name + "." + function_name + "$" + "LABEL" + str(self.label_counter) # create unique label name using format filename.functionname$LABELXXX
        self.write_push_pop("C_PUSH", "constant", new_label)
        self.reg_to_stack("LCL")
        self.reg_to_stack("ARG")
        self.reg_to_stack("THIS")
        self.reg_to_stack("THAT")
        # ARG = SP - num_args - 5
        self.output_file.write("@" + str(num_args) + "\n")
        self.output_file.write("D=A\n")
        self.output_file.write("@5\n")
        self.output_file.write("D=D+A\n")
        self.output_file.write("@SP\n")
        self.output_file.write("D=M-D\n")
        self.output_file.write("@ARG\n")
        self.output_file.write("M=D\n")
        # LCL = SP
        self.output_file.write("@SP\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@LCL\n")
        self.output_file.write("M=D\n")
        # goto function_name
        self.write_goto(function_name)
        # label
        self.write_label(new_label)

    # push value in specified register to stack
    def reg_to_stack(self, reg):
        self.output_file.write("@" + reg + "\n")
        self.output_file.write("D=M\n")
        self.push_d()

    # write function behavior
    ## parameters: function_name - name of function being defined; num_locals - number of local variables
    def write_function(self, function_name, num_locals):
        self.write_label(function_name)
        for i in range(int(num_locals)):
            self.write_push_pop("C_PUSH", "constant", 0)

    # write return behavior
    def write_return(self):
        self.output_file.write("@LCL\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@FRAME\n")
        self.output_file.write("M=D\n") # FRAME=LCL
        self.output_file.write("@5\n")
        self.output_file.write("A=D-A\n") # A=FRAME-5
        self.output_file.write("D=M\n") # D=*(FRAME-5)
        self.output_file.write("@RET\n")
        self.output_file.write("M=D\n") # RET=*(FRAME-5)
        self.output_file.write("@ARG\n")
        self.output_file.write("A=M\n")
        self.pop() # *ARG=pop()
        self.output_file.write("@ARG\n")
        self.output_file.write("D=M+1\n")
        self.output_file.write("@SP\n")
        self.output_file.write("M=D\n") # SP=ARG+1
        for reg in ('THAT', 'THIS', 'ARG', 'LCL'):
            self.restore_register(reg)
        self.output_file.write("@RET\n")
        self.output_file.write("A=M\n")
        self.output_file.write("0;JMP\n")

    # uses temp variable FRAME as a reference to restore register values. decrements value of FRAME by 1 each time.
    def restore_register(self, register):
        self.output_file.write("@FRAME\n")
        self.output_file.write("AM=M-1\n")
        self.output_file.write("D=M\n")
        self.output_file.write("@" + register + "\n")
        self.output_file.write("M=D\n")
