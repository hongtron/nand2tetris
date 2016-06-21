#!/usr/bin/env python
import string

class Code():
    comp_dict = {
        '0':'0101010',  '1':'0111111',  '-1':'0111010',
        'D':'0001100', '!D':'0001101', '-D':'0001111', 'D+1':'0011111', 'D-1':'0001110', 
        'A':'0110000', '!A':'0110001', '-A':'0110011', 'A+1':'0110111', 'A-1':'0110010',
        'M':'1110000', '!M':'1110001', '-M':'1110011', 'M+1':'1110111', 'M-1':'1110010',
        'D+A':'0000010', 'D-A':'0010011', 'A-D':'0000111', 'D&A':'0000000', 'D|A':'0010101',
        'D+M':'1000010', 'D-M':'1010011', 'M-D':'1000111', 'D&M':'1000000', 'D|M':'1010101'
    }

    jump_dict = {
        'nowhere':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011', 'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'
    }

    def __init__(self):
        pass
    
    def dest(self, dest_string):
        if dest_string == 'nowhere':
            return '000'
        dest_bits = ''
        if 'A' in dest_string:
            dest_bits += '1'
        else:
            dest_bits += '0'
        if 'D' in dest_string:
            dest_bits += '1'
        else:
            dest_bits += '0'
        if 'M' in dest_string:
            dest_bits += '1'
        else:
            dest_bits += '0'
        return dest_bits

    def comp(self, comp_string):
        return self.comp_dict[comp_string]

    def jump(self, jump_string):
        return self.jump_dict[jump_string]

    def int_to_binary(self, int_value):
        return string.zfill(bin(int_value)[2:], 16) # pad with zeros to 16 bits, and ignore first two characters since they are not part of the binary number

