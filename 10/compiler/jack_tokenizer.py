#!/usr/bin/env python


class JackTokenizer:
    # constructor: create a new tokenizer object; each new file should use a
    # new tokenizer.
    # parameters: input_file - the file currently being tokenized
    def __init__(self, input_file):
        self.input_file = open(input_file, 'r')
        self.working_input = self.clean(self.input_file)
        self.output_file = open(input_file.replace('.jack', 'T.xml'), 'w+')
        self.output_file.write('<tokens>\n')
        self.current_type = None
        self.current_keyword = None
        self.current_symbol = None
        self.current_identifier = None
        self.current_int_val = None
        self.current_string_val = None
        self.keywords = [
            'class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
            'this', 'let', 'do', 'if', 'else', 'while', 'return'
            ]
        self.xml_char_translator = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
        self.symbols = '{}()[].,;+-*/&|<>=~'

    # remove comments and whitespace, and store input file as a list of words
    # parameters: input_file - the file currently being tokenized
    def clean(self, input_file):
        working_string = ''
        # convert to string to facilitate multi-line comment removal later
        for line in input_file:
            # first, check for '//' comments, which depend on line context
            if '//' in line:  # check for comment
                # if found, ignore everything after the first instance of '//'
                line = line.split('//', 1)[0]
                # restore newline that got chopped off (so it can be properly
                # replaced with a space later)
                line += '\n'
            working_string = working_string + line
        # replace whitespaces with single spaces
        segments = working_string.split()
        working_string = ' '.join(segments)
        # convert '/**' comments to '/*' comments for easier removal
        if '/**' in working_string:
            working_string = working_string.replace('/**', '/*')
        # remove '/*' comments (i.e. all remaining comments)
        while '/*' in working_string:
            comment_start = working_string.find('/*')
            comment_end = working_string.find('*/') + 2
            working_string = working_string[:comment_start] + \
                working_string[comment_end:]
        return working_string.split(' ')

    # returns True if there is more input to tokenize, False o/w
    def has_more_tokens(self):
        if len(self.working_input) > 0:
            return True
        else:
            self.output_file.write('</tokens>\n')
            self.output_file.close()
            return False

    # get the next token from the input and make it the current token
    def advance(self):
        if self.has_more_tokens():
            current_token = self.clean_token()
            if current_token in self.keywords:
                self.current_type = 'KEYWORD'
                self.current_keyword = current_token.upper()
                self.current_symbol = None
                self.current_identifier = None
                self.current_int_val = None
                self.current_string_val = None
                self.write_tag()
            elif current_token in self.symbols:
                self.current_type = 'SYMBOL'
                self.current_keyword = None
                self.current_symbol = current_token
                self.current_identifier = None
                self.current_int_val = None
                self.current_string_val = None
                self.write_tag()
            elif current_token == '"':
                self.current_type = 'STRING_CONST'
                self.current_keyword = None
                self.current_symbol = None
                self.current_identifier = None
                self.current_int_val = None
                self.current_string_val = current_token
                string_word = self.working_input.pop(0)
                while string_word == '' or string_word.isspace():
                    string_word = self.working_input.pop(0)
                self.current_string_val += string_word
                while self.current_string_val[-1] != '"':
                    string_word = self.clean_token()
                    self.current_string_val += " " + string_word
                # omit quotes
                self.current_string_val = self.current_string_val[1:-1]
                self.write_tag()
            else:
                try:
                    int_val = int(current_token)
                    if 0 <= int_val <= 32767:
                        self.current_type = 'INT_CONST'
                        self.current_keyword = None
                        self.current_symbol = None
                        self.current_identifier = None
                        self.current_int_val = int_val
                        self.current_string_val = None
                        self.write_tag()
                    else:
                        raise StandardError('Integer value is invalid, or invalid \
                            identifier.')
                except ValueError:
                    good_id = True
                    for current_char in current_token:
                        if current_char in self.symbols:
                            good_id = False
                            tok_segs = current_token.partition(current_char)
                            if tok_segs[2] != '':
                                self.working_input.insert(0, tok_segs[2])
                            self.working_input.insert(0, tok_segs[1])
                            if tok_segs[0] != '':
                                self.working_input.insert(0, tok_segs[0])
                            self.advance()
                            break
                    if good_id:
                        self.current_type = 'IDENTIFIER'
                        self.current_keyword = None
                        self.current_symbol = None
                        self.current_identifier = current_token
                        self.current_int_val = None
                        self.current_string_val = None
                        self.write_tag()
            return current_token

    def clean_token(self):
        working_token = self.working_input.pop(0)
        while working_token == '' or working_token.isspace():
            working_token = self.working_input.pop(0)
        if '"' in working_token:
            for string_piece in working_token.partition('"')[::-1]:
                if not string_piece.isspace() and string_piece is not '':
                    self.working_input.insert(0, string_piece)
            working_token = self.working_input.pop(0)
        return working_token

    def push_token(self, token, identifier):
        self.working_input.insert(0, token)  # restore popped token
        self.current_type = 'IDENTIFIER'
        self.current_keyword = None
        self.current_symbol = None
        self.current_identifier = identifier
        self.current_int_val = None
        self.current_string_val = None
        # self.write_tag()

    def write_tag(self):
        if self.current_type == 'KEYWORD':
            self.output_file.write('<keyword> ' +
                                   self.current_keyword.lower() +
                                   ' </keyword>\n')
        elif self.current_type == 'SYMBOL':
            # convert <, >, and & for XML output
            if self.current_symbol in self.xml_char_translator:
                print_symbol = self.xml_char_translator[self.current_symbol]
            else:
                print_symbol = self.current_symbol
            self.output_file.write('<symbol> ' + print_symbol +
                                   ' </symbol>\n')
        elif self.current_type == 'STRING_CONST':
            self.output_file.write('<stringConstant> ' +
                                   self.current_string_val +
                                   ' </stringConstant>\n')
        elif self.current_type == 'INT_CONST':
            self.output_file.write('<integerConstant> ' +
                                   str(self.current_int_val) +
                                   ' </integerConstant>\n')
        elif self.current_type == 'IDENTIFIER':
            self.output_file.write('<identifier> ' + self.current_identifier +
                                   ' </identifier>\n')

    def token_type(self):
        return self.current_type

    def keyword(self):
        return self.current_keyword

    def symbol(self):
        return self.current_symbol

    def identifier(self):
        return self.current_identifier

    def int_val(self):
        return self.current_int_val

    def string_val(self):
        return self.current_string_val
