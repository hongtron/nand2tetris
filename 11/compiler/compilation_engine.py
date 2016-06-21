#!/usr/bin/env python


# reads input from a JackTokenizer and uses a VMWriter to generate output
class CompilationEngine:
    # constructor
    def __init__(self, tokenizer, table, writer):
        self.tokenizer = tokenizer
        self.table = table
        self.writer = writer
        self.loop_counter = {'IF': 0, 'WHILE': 0}
        self.segment_translator = {'STATIC': 'static', 'FIELD': 'this',
                                   'ARG': 'argument', 'VAR': 'local'}
        self.bin_ops_translator = {'+': 'add', '-': 'sub', '=': 'eq', '>': 'gt',
                                   '<': 'lt', '&': 'and', '|': 'or',
                                   '*': 'call Math.multiply 2',
                                   '/': 'call Math.divide 2'}
        self.unary_ops_translator = {'-': 'neg', '~': 'not'}

    # compile the class defined in the current input file; called by JackCompiler
    def compile_class(self):
        self.tokenizer.advance()
        # 'class' keyword
        self.verify_token('KEYWORD', 'CLASS')
        self.tokenizer.advance()
        # class name
        self.verify_token('IDENTIFIER')
        self.current_class = self.tokenizer.identifier()
        self.tokenizer.advance()
        # {
        self.verify_token('SYMBOL', '{')
        # class_var_dec* subroutine_dec*
        self.tokenizer.advance()
        while self.tokenizer.current_type == 'KEYWORD':
            # class_var_dec (vars can be scoped as 'static' or 'field')
            if self.tokenizer.keyword() in ('STATIC', 'FIELD'):
                self.compile_class_var_dec()
            # subroutine_dec (a subroutine can be constructor, function, or method)
            elif self.tokenizer.keyword() in ('CONSTRUCTOR', 'FUNCTION',
                                              'METHOD'):
                self.compile_subroutine()
            # throw error for unexpected keyword
            else:
                self.verify_token('KEYWORD', ('STATIC', 'FIELD', 'CONSTRUCTOR',
                                  'FUNCTION', 'METHOD'))
        # }
        self.verify_token('SYMBOL', '}')
        # finish up
        self.writer.close()
        self.tokenizer.advance()

    # compile variable declaration for a class
    def compile_class_var_dec(self):
        # static | field
        self.verify_token('KEYWORD', ('STATIC', 'FIELD'))
        # store variable kind (either 'static' or 'field') to be stored in symbol table
        context = self.tokenizer.keyword()
        self.tokenizer.advance()
        # (type var_name)(',' var_name)* ;
        self.multiple_variables(';', context)
        self.tokenizer.advance()

    # handle (type var_name)(',' var_name)*
    # stop when end_symbol is encountered
    # context is either 'var', 'field', or 'static'
    # can't be used for 'arg' because type is not explicit for each variable here
    # used by compile_class_var_dec and compile_var_dec
    def multiple_variables(self, end_symbol, context):
        # keep track of number of variables in case caller is compile_var_dec
        num_variables = 0
        # type
        type = self.type_helper()
        # var_name
        self.verify_token('IDENTIFIER')
        # store in symbol table, increment counter
        self.table.define(self.tokenizer.identifier(), context, type)
        num_variables += 1
        self.tokenizer.advance()
        # (',' var_name)*
        self.verify_token('SYMBOL', (',', end_symbol))
        # loop until end_symbol is encountered
        while self.tokenizer.current_symbol == ',':
            num_variables += 1
            self.tokenizer.advance()
            self.verify_token('IDENTIFIER')
            # store in symbol table
            self.table.define(self.tokenizer.identifier(), context, type)
            self.tokenizer.advance()
            self.verify_token('SYMBOL', (',', end_symbol))
        return num_variables

    # confirm that variable type is being correctly defined where appropriate,
    # and return that type
    def type_helper(self):
        # native type
        if self.tokenizer.token_type() == 'KEYWORD':
            self.verify_token('KEYWORD', ('INT', 'CHAR', 'BOOLEAN'))
            type = self.tokenizer.keyword()
        # class type
        else:
            # class name, not stored in symbol table
            self.verify_token('IDENTIFIER')
            type = self.tokenizer.identifier()
        self.tokenizer.advance()
        return type

    # compile a subroutine defined in the class
    def compile_subroutine(self):
        # keep track of whether subroutine is void so we know whether to push 0 at the end
        is_void = False
        # clear subroutine scope in symbol table before starting new subroutine
        self.table.start_subroutine()
        # reset loop counters for conditionals
        # (okay because VM implementation writes function_name$label)
        self.loop_counter = {'IF': 0, 'WHILE': 0}
        # constructor | function | method
        self.verify_token('KEYWORD', ('CONSTRUCTOR', 'FUNCTION', 'METHOD'))
        # store type of subroutine
        subroutine_type = self.tokenizer.keyword()
        # argument 0 of a method always refers to the 'this' object
        # (i.e. reference to the object on which the method is supposed to operate)
        if subroutine_type == 'METHOD':
            self.table.define('this', 'ARG', self.current_class)
        self.tokenizer.advance()
        # void | type
        if self.tokenizer.token_type() == 'KEYWORD' and \
                self.tokenizer.keyword() == 'VOID':
            is_void = True
            self.tokenizer.advance()
        else:
            self.type_helper()
        # subroutine name
        self.verify_token('IDENTIFIER')
        self.current_subroutine = self.tokenizer.identifier()
        self.tokenizer.advance()
        # (
        self.verify_token('SYMBOL', '(')
        self.tokenizer.advance()
        # parameter list
        self.compile_parameter_list()
        # )
        self.verify_token('SYMBOL', ')')
        self.tokenizer.advance()
        # subroutine body
        self.compile_subroutine_body(is_void, subroutine_type)
        self.tokenizer.advance()

    # compile subroutine's parameter list
    def compile_parameter_list(self):
        # ( ... )?
        while self.tokenizer.token_type() != 'SYMBOL' and \
                self.tokenizer.symbol() != ')':
            self.verify_token(('KEYWORD', 'IDENTIFIER'))
            # type
            type = self.type_helper()
            # var_name
            self.verify_token('IDENTIFIER')
            # store in symbol table
            # these are arguments expected by the function being defined
            self.table.define(self.tokenizer.identifier(), 'ARG', type)
            self.tokenizer.advance()
            if self.tokenizer.token_type() == 'SYMBOL' and \
                    self.tokenizer.symbol() == ',':
                self.tokenizer.advance()

    # compile body of subroutine
    def compile_subroutine_body(self, is_void, subroutine_type):
        # {
        self.verify_token('SYMBOL', '{')
        self.tokenizer.advance()
        # var_dec
        n_locals = self.compile_var_dec()
        # write function <class_name>.<subroutine_name>
        function_name = self.current_class + "." + self.current_subroutine
        self.writer.write_function(function_name, n_locals)
        if subroutine_type == 'CONSTRUCTOR':
            # calculate number of field vars for memory allocation
            self.writer.write_push('constant', self.table.var_count('FIELD'))
            # allocate space based on size required, and leave address on stack
            self.writer.write_call('Memory.alloc', 1)
            # set base of the 'this' segment to the returned address
            self.writer.write_pop('pointer', 0)
        elif subroutine_type == 'METHOD':
            # set base of 'this' segment
            # (argument 0 was defined as 'this' in compile_subroutine)
            self.writer.write_push('argument', 0)
            self.writer.write_pop('pointer', 0)
        else:  # 'FUNCTION'
            # no additional action required
            pass
        # statements
        self.compile_statements(is_void)
        # }
        self.verify_token('SYMBOL', '}')

    def compile_var_dec(self):
        # these are local variables; need to keep track of count because it will
        # be included in the 'function' command
        n_locals = 0
        while self.tokenizer.token_type() == 'KEYWORD' and \
                self.tokenizer.keyword() == 'VAR':
            # var
            self.verify_token('KEYWORD', 'VAR')
            self.tokenizer.advance()
            # type varName (',' varName)* ;
            n_locals += self.multiple_variables(';', 'VAR')
            self.tokenizer.advance()
        return n_locals

    def compile_statements(self, is_void):
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
                if is_void:
                    self.writer.write_push('constant', 0)
                self.compile_return()

    def compile_let(self):
        # let
        self.verify_token('KEYWORD', 'LET')
        self.tokenizer.advance()
        # var name
        self.verify_token('IDENTIFIER')
        var_name = self.tokenizer.identifier()
        array = False
        memory_loc = self.map_var_to_memory(var_name)
        self.tokenizer.advance()
        # array
        # ('[' expression ']')?
        if self.tokenizer.token_type() == 'SYMBOL' and \
                self.tokenizer.symbol() == '[':
            array = True
            # [
            self.tokenizer.advance()
            # push base address
            self.writer.write_push(memory_loc[0], memory_loc[1])
            # expression
            # leaves array index on top of stack
            self.compile_expression()
            # ]
            self.verify_token('SYMBOL', ']')
            # leave base address + array index on top of stack
            self.writer.write_arithmetic('add')
            self.tokenizer.advance()
        # =
        self.verify_token('SYMBOL', '=')
        self.tokenizer.advance()
        # expression
        self.compile_expression()
        # ;
        self.verify_token('SYMBOL', ';')
        if array:
            # result of expression is on top of stack
            # base address + array index is underneath that
            self.writer.write_pop('temp', 0)
            self.writer.write_pop('pointer', 1)
            self.writer.write_push('temp', 0)
            self.writer.write_pop('that', 0)
        else:
            self.writer.write_pop(memory_loc[0], memory_loc[1])
        self.tokenizer.advance()

    def compile_if(self):
        current_loop = self.compile_key_exp_stat_syntax('IF')
        # (else ...)?
        if self.tokenizer.keyword() == 'ELSE':
            # else
            self.tokenizer.advance()
            # {
            self.verify_token('SYMBOL', '{')
            self.tokenizer.advance()
            # statements
            self.writer.write_label('IF_FALSE' + str(current_loop))
            self.compile_statements(False)  # void not applicable here
            # }
            self.verify_token('SYMBOL', '}')
            self.tokenizer.advance()
        else:
            self.writer.write_label('IF_FALSE' + str(current_loop))
        self.writer.write_label('IF_END' + str(current_loop))

    def compile_while(self):
        self.compile_key_exp_stat_syntax('WHILE')

    # used by 'if' and 'while'
    def compile_key_exp_stat_syntax(self, keyword):
        if keyword == 'IF':
            current_loop = self.loop_counter['IF']
            self.loop_counter['IF'] += 1
        elif keyword == 'WHILE':
            current_loop = self.loop_counter['WHILE']
            self.loop_counter['WHILE'] += 1
        # keyword
        self.verify_token('KEYWORD', keyword)
        self.tokenizer.advance()
        # (
        self.verify_token('SYMBOL', '(')
        self.tokenizer.advance()
        # expression
        if keyword == 'WHILE':
            self.writer.write_label('WHILE_EXP' + str(current_loop))
        self.compile_expression()
        # ~(cond)
        if keyword == 'WHILE':
            self.writer.write_arithmetic('not')
        if keyword == 'WHILE':
            self.writer.write_if('WHILE_END' + str(current_loop))
        elif keyword == 'IF':
            self.writer.write_if('IF_TRUE' + str(current_loop))
            self.writer.write_goto('IF_FALSE' + str(current_loop))
            self.writer.write_label('IF_TRUE' + str(current_loop))
        # )
        self.verify_token('SYMBOL', ')')
        self.tokenizer.advance()
        # {
        self.verify_token('SYMBOL', '{')
        self.tokenizer.advance()
        # statements
        self.compile_statements(False)  # void not applicable here
        if keyword == 'WHILE':
            self.writer.write_goto('WHILE_EXP' + str(current_loop))
            self.writer.write_label('WHILE_END' + str(current_loop))
        elif keyword == 'IF':
            self.writer.write_goto('IF_END' + str(current_loop))
        # }
        self.verify_token('SYMBOL', '}')
        self.tokenizer.advance()
        return current_loop

    def compile_do(self):
        # do
        self.verify_token('KEYWORD', 'DO')
        self.tokenizer.advance()
        # subroutine call
        self.compile_subroutine_call()
        # ;
        self.verify_token('SYMBOL', ';')
        self.tokenizer.advance()
        self.writer.write_pop('temp', 0)  # pop and ignore

    def compile_return(self):
        # return
        self.verify_token('KEYWORD', 'RETURN')
        self.tokenizer.advance()
        # expression?
        if self.tokenizer.token_type() != 'SYMBOL' and \
                self.tokenizer.symbol != ';':
            self.compile_expression()
        # ;
        self.verify_token('SYMBOL', ';')
        self.tokenizer.advance()
        self.writer.write_return()

    def compile_expression(self):
        self.compile_term()
        # (op term)*
        while self.tokenizer.token_type() == 'SYMBOL' and \
                self.tokenizer.symbol() in ('+', '-', '*', '/', '&', '|',
                                            '<', '>', '='):
            # op
            operation = self.bin_ops_translator[self.tokenizer.symbol()]
            self.tokenizer.advance()
            # term
            self.compile_term()
            self.writer.write_arithmetic(operation)

    def compile_term(self):
        # if identifier, need a look-ahead
        if self.tokenizer.token_type() == 'IDENTIFIER':
            hold_identifier = self.tokenizer.identifier()
            popped_token = self.tokenizer.advance()
            if self.tokenizer.token_type() == 'SYMBOL':
                if self.tokenizer.symbol() == '[':
                    # array
                    self.tokenizer.push_token(popped_token, hold_identifier)
                    # push array pointer (i.e. base address)
                    memory_loc = self.map_var_to_memory(self.tokenizer.identifier())
                    self.writer.write_push(memory_loc[0], memory_loc[1])
                    self.tokenizer.advance()
                    # [
                    self.verify_token('SYMBOL', '[')
                    self.tokenizer.advance()
                    # expression
                    self.compile_expression()
                    # ]
                    self.verify_token('SYMBOL', ']')
                    # add index that is the result of the expression to the base address
                    self.writer.write_arithmetic('add')
                    # pop resulting address to 'that'
                    self.writer.write_pop('pointer', 1)
                    # push reference
                    self.writer.write_push('that', 0)
                    self.tokenizer.advance()
                elif self.tokenizer.symbol() in ('(', '.'):
                    # subroutine call
                    self.tokenizer.push_token(popped_token, hold_identifier)
                    self.compile_subroutine_call()
                else:
                    # identifier
                    self.tokenizer.push_token(popped_token, hold_identifier)
                    memory_loc = self.map_var_to_memory(self.tokenizer.identifier())
                    self.writer.write_push(memory_loc[0], memory_loc[1])
                    self.tokenizer.advance()
        elif self.tokenizer.token_type() in ('KEYWORD', 'STRING_CONST',
                                             'INT_CONST'):
            # string const, int const, or keyword const
            self.write_constant()
            self.tokenizer.advance()
        else:
            # symbol
            self.verify_token('SYMBOL')
            if self.tokenizer.symbol() == '(':
                # '(' expression ')'
                self.tokenizer.advance()
                self.compile_expression()
                self.verify_token('SYMBOL', ')')
                self.tokenizer.advance()
            elif self.tokenizer.symbol() in ('-', '~'):
                # unary op
                operation = self.unary_ops_translator[self.tokenizer.symbol()]
                self.tokenizer.advance()
                # term
                self.compile_term()
                self.writer.write_arithmetic(operation)
            else:
                # throw error for unexpected symbol
                self.verify_token('SYMBOL', ('(', '-', '~'))

    def write_constant(self):
        if self.tokenizer.token_type() == 'KEYWORD':
            self.verify_token('KEYWORD', ('TRUE', 'FALSE', 'NULL', 'THIS'))
            if self.tokenizer.keyword() == 'TRUE':
                self.writer.write_push('constant', 0)
                self.writer.write_arithmetic('not')
            elif self.tokenizer.keyword() in ('FALSE', 'NULL'):
                self.writer.write_push('constant', 0)
            else:  # this
                self.writer.write_push('pointer', 0)
        elif self.tokenizer.token_type() == 'STRING_CONST':
            string_value = self.tokenizer.string_val()
            self.writer.write_push('constant', len(string_value))
            self.writer.write_call('String.new', 1)
            for letter in string_value:
                unicode_equiv = ord(letter)
                self.writer.write_push('constant', unicode_equiv)
                self.writer.write_call('String.appendChar', 2)
        else:
            # int constant
            self.writer.write_push('constant', self.tokenizer.int_val())

    def compile_expression_list(self):
        n_args = 0  # count number of arguments for subroutine call
        while self.tokenizer.symbol() != ')':
            n_args += 1
            self.compile_expression()
            if self.tokenizer.token_type() == 'SYMBOL' and \
                    self.tokenizer.symbol() == ',':
                self.tokenizer.advance()
        return n_args

    def compile_subroutine_call(self):
        # subroutine name | class name | var name
        # need look-ahead to determine which one
        self.verify_token('IDENTIFIER')
        # start building string to determine how subroutine will be called
        # based on its type
        subroutine_name = ''
        # store state in preparation for look-ahead
        hold_identifier = self.tokenizer.identifier()
        popped_token = self.tokenizer.advance()
        self.verify_token('SYMBOL')
        if self.tokenizer.symbol() == '(':
            # method
            # subroutineName '(' expressionList ')'
            n_args = 1  # first argument for method always refers to 'this' object
            subroutine_name += self.current_class + '.'
            self.tokenizer.push_token(popped_token, hold_identifier)
            # subroutine name
            subroutine_name += self.tokenizer.identifier()
            self.tokenizer.advance()
            # (
            self.verify_token('SYMBOL', '(')
            self.tokenizer.advance()
            # push 'this' pointer
            self.writer.write_push('pointer', 0)
            # expression list
            n_args += self.compile_expression_list()
            # )
            self.verify_token('SYMBOL', ')')
        elif self.tokenizer.symbol() == '.':
            # (className | varName) '.' subroutineName '(' expressionList ')'
            self.tokenizer.push_token(popped_token, hold_identifier)
            if self.table.lookup(self.tokenizer.identifier()) == 'NONE':
                # function or constructor
                # className, not stored in symbol table
                n_args = 0
                subroutine_name += self.tokenizer.identifier() + '.'
            else:
                # method
                # varName
                subroutine_name += self.table.type_of(self.tokenizer.identifier()) + '.'
                n_args = 1  # first argument for method always refers to 'this' object
                memory_loc = self.map_var_to_memory(self.tokenizer.identifier())
                # push 'this' pointer
                self.writer.write_push(memory_loc[0], memory_loc[1])
            self.tokenizer.advance()
            # .
            self.tokenizer.advance()
            # subroutine name, not stored in symbol table
            self.verify_token('IDENTIFIER')
            subroutine_name += self.tokenizer.identifier()
            self.tokenizer.advance()
            # (
            self.verify_token('SYMBOL', '(')
            self.tokenizer.advance()
            # expression list
            n_args += self.compile_expression_list()
            # )
            self.verify_token('SYMBOL', ')')
        else:
            # throw error for unexpected symbol
            self.tokenizer.push_token(popped_token, hold_identifier)
            self.tokenizer.advance()
            self.verify_token('SYMBOL', ('(', '.'))
        self.writer.write_call(subroutine_name, n_args)
        self.tokenizer.advance()

    # return tuple containing the segment and index corresponding to a stored symbol
    def map_var_to_memory(self, var_name):
        segment = self.segment_translator[self.table.kind_of(var_name)]
        index = self.table.index_of(var_name)
        return (segment, index)

    # function used to verify grammar of input from JackTokenizer
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
