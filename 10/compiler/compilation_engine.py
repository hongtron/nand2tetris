#!/usr/bin/env python


class CompilationEngine:
    # constructor: used to emit structured XML output from token stream
    # parameters: input_file - token input; output_file - XML output
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output_file = open(output_file, "w+")
        self.current_depth = 0
        self.non_terminals = []
        self.xml_char_translator = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}

    # compile XML output for class
    def compile_class(self):
        self.tokenizer.advance()
        self.open_non_terminal('class')
        self.verify_token('KEYWORD', 'CLASS')
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # class name
        self.verify_token('IDENTIFIER')
        self.write_terminal('IDENTIFIER')
        self.tokenizer.advance()
        # {
        self.verify_token('SYMBOL', '{')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        while self.tokenizer.current_type == 'KEYWORD':
            # class var dec
            if self.tokenizer.keyword() in ('STATIC', 'FIELD'):
                self.compile_class_var_dec()
            # subroutine dec
            elif self.tokenizer.keyword() in ('CONSTRUCTOR', 'FUNCTION',
                                              'METHOD'):
                self.compile_subroutine()
            # throw error if unexpected keyword
            else:
                self.verify_token('KEYWORD', ('STATIC', 'FIELD', 'CONSTRUCTOR',
                                  'FUNCTION', 'METHOD'))
        self.verify_token('SYMBOL', '}')
        self.write_terminal('SYMBOL')
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_class_var_dec(self):
        self.open_non_terminal('classVarDec')
        # static | field
        self.verify_token('KEYWORD', ('STATIC', 'FIELD'))
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        self.multiple_variables(';')
        # ;
        self.write_terminal('SYMBOL')
        # </classVarDec>
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_subroutine(self):
        self.open_non_terminal('subroutineDec')
        # constructor | function | method
        self.verify_token('KEYWORD', ('CONSTRUCTOR', 'FUNCTION', 'METHOD'))
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # void | type
        if self.tokenizer.token_type() == 'KEYWORD' and \
                self.tokenizer.keyword() == 'VOID':
            self.write_terminal('KEYWORD')
            self.tokenizer.advance()
        else:
            self.type_helper()
        # subroutine name
        self.verify_token('IDENTIFIER')
        self.write_terminal('IDENTIFIER')
        self.tokenizer.advance()
        # (
        self.verify_token('SYMBOL', '(')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # parameter list
        self.compile_parameter_list()
        # )
        self.verify_token('SYMBOL', ')')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # subroutine body
        self.open_non_terminal("subroutineBody")
        # {
        self.verify_token('SYMBOL', '{')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # varDec
        while self.tokenizer.token_type() == 'KEYWORD' and \
                self.tokenizer.keyword() == 'VAR':
            self.compile_var_dec()
        # statements
        self.compile_statements()
        # }
        self.verify_token('SYMBOL', '}')
        self.write_terminal('SYMBOL')
        # </subroutineBody>
        self.close_non_terminal()
        # </subroutineDec>
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_parameter_list(self):
        self.open_non_terminal("parameterList")
        while self.tokenizer.token_type() != 'SYMBOL' and \
                self.tokenizer.symbol() != ')':
            self.verify_token(('KEYWORD', 'IDENTIFIER'))
            # type
            self.type_helper()
            # var name
            self.verify_token('IDENTIFIER')
            self.write_terminal('IDENTIFIER')
            self.tokenizer.advance()
            if self.tokenizer.token_type() == 'SYMBOL' and \
                    self.tokenizer.symbol() == ',':
                self.write_terminal('SYMBOL')
                self.tokenizer.advance()
        self.close_non_terminal()

    def compile_var_dec(self):
        self.open_non_terminal("varDec")
        self.verify_token('KEYWORD', 'VAR')
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # type varName (',' varName)*
        self.multiple_variables(';')
        # ;
        self.write_terminal('SYMBOL')
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_statements(self):
        self.open_non_terminal("statements")
        self.verify_token('KEYWORD',
                          ('LET', 'IF', 'WHILE', 'DO', 'RETURN'))
        while self.tokenizer.token_type() == 'KEYWORD':
            if self.tokenizer.keyword() == 'LET':
                self.compile_let()
            elif self.tokenizer.keyword() == 'IF':
                self.compile_if()
            elif self.tokenizer.keyword() == 'WHILE':
                self.compile_while()
            elif self.tokenizer.keyword() == 'DO':
                self.compile_do()
            elif self.tokenizer.keyword() == 'RETURN':
                self.compile_return()
        self.close_non_terminal()

    def compile_let(self):
        self.open_non_terminal('letStatement')
        # let
        self.verify_token('KEYWORD', 'LET')
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # var name
        self.verify_token('IDENTIFIER')
        self.write_terminal('IDENTIFIER')
        self.tokenizer.advance()
        # ('[' expression ']')?
        if self.tokenizer.token_type() == 'SYMBOL' and \
                self.tokenizer.symbol() == '[':
            # [
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            # expression
            self.compile_expression()
            # ]
            self.verify_token('SYMBOL', ']')
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
        # =
        self.verify_token('SYMBOL', '=')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # expression
        self.compile_expression()
        # ;
        self.verify_token('SYMBOL', ';')
        self.write_terminal('SYMBOL')
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_if(self):
        self.open_non_terminal('ifStatement')
        self.compile_key_exp_stat_syntax('IF')
        # (else ...)?
        if self.tokenizer.keyword() == 'ELSE':
            # else
            self.write_terminal('KEYWORD')
            self.tokenizer.advance()
            # {
            self.verify_token('SYMBOL', '{')
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            # statements
            self.compile_statements()
            # }
            self.verify_token('SYMBOL', '}')
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
        self.close_non_terminal()

    def compile_while(self):
        self.open_non_terminal('whileStatement')
        self.compile_key_exp_stat_syntax('WHILE')
        self.close_non_terminal()

    def compile_do(self):
        self.open_non_terminal('doStatement')
        # do
        self.verify_token('KEYWORD', 'DO')
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # subroutine call
        self.compile_subroutine_call()
        # ;
        self.verify_token('SYMBOL', ';')
        self.write_terminal('SYMBOL')
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_return(self):
        # return
        self.open_non_terminal('returnStatement')
        # do
        self.verify_token('KEYWORD', 'RETURN')
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # expression?
        if self.tokenizer.token_type() != 'SYMBOL' and \
                self.tokenizer.symbol != ';':
            self.compile_expression()
        # ;
        self.verify_token('SYMBOL', ';')
        self.write_terminal('SYMBOL')
        self.close_non_terminal()
        self.tokenizer.advance()

    def compile_expression(self):
        self.open_non_terminal('expression')
        self.compile_term()
        # (op term)*
        while self.tokenizer.token_type() == 'SYMBOL' and \
                self.tokenizer.symbol() in ('+', '-', '*', '/', '&', '|',
                                            '<', '>', '='):
            # op
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            # term
            self.compile_term()
        self.close_non_terminal()

    def compile_term(self):
        self.open_non_terminal('term')
        # if identifier, need a look-ahead
        if self.tokenizer.token_type() == 'IDENTIFIER':
            hold_identifier = self.tokenizer.identifier()
            popped_token = self.tokenizer.advance()
            if self.tokenizer.token_type() == 'SYMBOL':
                if self.tokenizer.symbol() == '[':
                    # array
                    self.tokenizer.push_token(popped_token, hold_identifier)
                    self.write_terminal('IDENTIFIER')
                    self.tokenizer.advance()
                    self.verify_token('SYMBOL', '[')
                    self.write_terminal('SYMBOL')
                    self.tokenizer.advance()
                    self.compile_expression()
                    self.verify_token('SYMBOL', ']')
                    self.write_terminal('SYMBOL')
                    self.tokenizer.advance()
                elif self.tokenizer.symbol() in ('(', '.'):
                    # subroutine call
                    self.tokenizer.push_token(popped_token, hold_identifier)
                    self.compile_subroutine_call()
                else:
                    # identifier
                    self.tokenizer.push_token(popped_token, hold_identifier)
                    self.write_terminal('IDENTIFIER')
                    self.tokenizer.advance()
        elif self.tokenizer.token_type() in ('KEYWORD', 'STRING_CONST',
                                             'INT_CONST'):
            self.write_terminal(self.tokenizer.token_type())
            self.tokenizer.advance()
        else:
            # symbol
            self.verify_token('SYMBOL')
            if self.tokenizer.symbol() == '(':
                # '(' expression ')'
                self.write_terminal('SYMBOL')
                self.tokenizer.advance()
                self.compile_expression()
                self.verify_token('SYMBOL', ')')
                self.write_terminal('SYMBOL')
                self.tokenizer.advance()
            elif self.tokenizer.symbol() in ('-', '~'):
                # unary op
                self.write_terminal('SYMBOL')
                # term
                self.compile_term()
            else:
                # throw error for unexpected symbol
                self.verify_token('SYMBOL', ('(', '-', '~'))
        self.close_non_terminal()

    def compile_expression_list(self):
        self.open_non_terminal('expressionList')
        while self.tokenizer.symbol() != ')':
            self.compile_expression()
            if self.tokenizer.token_type() == 'SYMBOL' and \
                    self.tokenizer.symbol() == ',':
                self.write_terminal('SYMBOL')
                self.tokenizer.advance()
        self.close_non_terminal()

    def compile_subroutine_call(self):
        # subroutine name | class name | var name
        self.verify_token('IDENTIFIER')
        self.write_terminal('IDENTIFIER')
        self.tokenizer.advance()
        self.verify_token('SYMBOL')
        if self.tokenizer.symbol() == '(':
            # (
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            # expression list
            self.compile_expression_list()
            # )
            self.verify_token('SYMBOL', ')')
            self.write_terminal('SYMBOL')
        elif self.tokenizer.symbol() == '.':
            # .
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            # subroutine name
            self.verify_token('IDENTIFIER')
            self.write_terminal('IDENTIFIER')
            self.tokenizer.advance()
            # (
            self.verify_token('SYMBOL', '(')
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            # expression list
            self.compile_expression_list()
            # )
            self.verify_token('SYMBOL', ')')
            self.write_terminal('SYMBOL')
        else:
            # throw error for unexpected symbol
            self.verify_token('SYMBOL', ('(', '.'))
        self.tokenizer.advance()

    def compile_key_exp_stat_syntax(self, keyword):
        # keyword
        self.verify_token('KEYWORD', keyword)
        self.write_terminal('KEYWORD')
        self.tokenizer.advance()
        # (
        self.verify_token('SYMBOL', '(')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # expression
        self.compile_expression()
        # )
        self.verify_token('SYMBOL', ')')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # {
        self.verify_token('SYMBOL', '{')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()
        # statements
        self.compile_statements()
        # }
        self.verify_token('SYMBOL', '}')
        self.write_terminal('SYMBOL')
        self.tokenizer.advance()

    # handle (type varName)(',' varName)*
    # write (type varName) until end_symbol is encountered
    # do not output end_symbol
    def multiple_variables(self, end_symbol):
        # type
        self.type_helper()
        # var name
        self.verify_token('IDENTIFIER')
        self.write_terminal('IDENTIFIER')
        self.tokenizer.advance()
        # (',' varName)*
        self.verify_token('SYMBOL', (',', end_symbol))
        while self.tokenizer.current_symbol == ',':
            self.write_terminal('SYMBOL')
            self.tokenizer.advance()
            self.verify_token('IDENTIFIER')
            self.write_terminal('IDENTIFIER')
            self.tokenizer.advance()
            self.verify_token('SYMBOL', (',', end_symbol))

    def open_non_terminal(self, tag):
        self.non_terminals.append(tag)
        for i in range(self.current_depth):
            self.output_file.write('\t')
        self.output_file.write('<' + tag + '>\n')
        self.current_depth += 1

    def close_non_terminal(self):
        self.current_depth -= 1
        for i in range(self.current_depth):
            self.output_file.write('\t')
        self.output_file.write('</' + self.non_terminals.pop() + '>\n')

    def write_terminal(self, term_type):
        for i in range(self.current_depth):
            self.output_file.write('\t')
        if term_type == 'KEYWORD':
            self.output_file.write('<keyword> ' +
                                   self.tokenizer.keyword().lower() +
                                   ' </keyword>')
        elif term_type == 'SYMBOL':
            if self.tokenizer.symbol() in self.xml_char_translator:
                print_sym = self.xml_char_translator[self.tokenizer.symbol()]
            else:
                print_sym = self.tokenizer.symbol()
            self.output_file.write('<symbol> ' + print_sym +
                                   ' </symbol>')
        elif term_type == 'INT_CONST':
            self.output_file.write('<integerConstant> ' +
                                   str(self.tokenizer.int_val()) +
                                   ' </integerConstant>')
        elif term_type == 'STRING_CONST':
            self.output_file.write('<stringConstant> ' +
                                   self.tokenizer.string_val() +
                                   ' </stringConstant>')
        elif term_type == 'IDENTIFIER':
            self.output_file.write('<identifier> ' +
                                   self.tokenizer.identifier() +
                                   ' </identifier>')
        self.output_file.write('\n')

    def type_helper(self):
        if self.tokenizer.token_type() == 'KEYWORD':
            self.verify_token('KEYWORD', ('INT', 'CHAR', 'BOOLEAN'))
            self.write_terminal('KEYWORD')
        else:
            self.verify_token('IDENTIFIER')
            self.write_terminal('IDENTIFIER')
        self.tokenizer.advance()

    def verify_token(self, expected_type, expected_vals=None):
        if self.tokenizer.token_type() not in expected_type \
                and expected_vals is None:
            raise StandardError('Expected type ' + expected_type +
                                ' but found type ' +
                                self.tokenizer.token_type())
        elif expected_type == 'KEYWORD' and expected_vals is not None:
            if self.tokenizer.keyword() not in expected_vals:
                raise StandardError('Expected one of these keywords: ' +
                                    str(expected_vals) + ' but found ' +
                                    self.tokenizer.keyword())

        elif expected_type == 'SYMBOL' and expected_vals is not None:
            if self.tokenizer.symbol() not in expected_vals:
                raise StandardError('Expected one of these symbols: ' +
                                    str(expected_vals) + ' but found ' +
                                    self.tokenizer.symbol())
