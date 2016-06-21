#!/usr/bin/env python

import parser, code, sys, symbol_table

class Assembler():

    def __init__(self):
        self.cde = code.Code()
        self.symbols = symbol_table.SymbolTable()

    def first_pass(self, input_file):
        prs = parser.Parser(input_file, False) # don't strip pseudocommands
        instruction_line = -1
        while prs.has_more_commands():
            prs.advance()
            if prs.command_type() != 'L_COMMAND':
                instruction_line += 1 # only increment if A or C command
            else:
                self.symbols.add_entry(prs.cur_cmd.symbol, instruction_line + 1) # otherwise create entry in symbol table

    def second_pass(self, input_file):
        output_file = (input_file.rsplit('.asm', 1))[0] + '.hack'
        prs = parser.Parser(input_file, True) # do strip pseudocommands
        next_address = 16 # start allocating addresses at 16
        with open(output_file, 'w+') as outfile:
            while prs.has_more_commands():
                machine_line = ''
                prs.advance()
                if prs.command_type() == 'A_COMMAND':
                    symbol = prs.symbol()
                    if type(symbol) is int:
                        machine_line += self.cde.int_to_binary(symbol)
                    else:
                        if self.symbols.contains(symbol):
                            machine_line += self.cde.int_to_binary(self.symbols.get_address(symbol))
                        else:
                            self.symbols.add_entry(symbol, next_address)
                            machine_line += self.cde.int_to_binary(next_address)
                            next_address += 1
                else: # C command
                    machine_line += '111'
                    machine_line += self.cde.comp(prs.comp())
                    machine_line += self.cde.dest(prs.dest())
                    machine_line += self.cde.jump(prs.jump())
                outfile.write(machine_line + '\n')

def main():
    filein = sys.argv[1]
    assembler = Assembler()
    assembler.first_pass(filein)
    assembler.second_pass(filein)

main()
