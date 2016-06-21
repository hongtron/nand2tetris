#!/usr/bin/env python
import string

# organize command into its 3 main components: type, arg1, and arg2
class Command:
    def __init__(self, command):
        cmd_array = string.split(command, " ")
        keyword = cmd_array[0]
        arithmetic_keywords = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        two_arg_keywords = ["push", "pop", "function", "call"]
        if keyword in arithmetic_keywords:
            self.c_type = "C_ARITHMETIC"
            self.arg1 = keyword
            self.arg2 = None
        elif keyword in two_arg_keywords:
            self.c_type = "C_" + keyword.upper()
            self.arg1 = cmd_array[1]
            self.arg2 = cmd_array[2]
        elif keyword == "return":
            self.c_type = "C_RETURN"
            self.arg1 = None
            self.arg2 = None
        else:
            self.arg1 = cmd_array[1]
            self.arg2 = None
            if keyword == "label" or keyword == "goto":
                self.c_type = "C_" + keyword.upper()
            else:
                self.c_type = "C_IF"