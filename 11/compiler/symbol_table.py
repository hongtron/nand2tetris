#!/usr/bin/env python


# associates identifier names in program with identifier properties (type, kind, index)
# needed for compilation
class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.indices = {
            'STATIC': 0, 'FIELD': 0, 'ARG': 0, 'VAR': 0
        }

    # reset subroutine symbol table
    def start_subroutine(self):
        self.subroutine_table.clear()
        self.indices['ARG'] = 0
        self.indices['VAR'] = 0

    def define(self, name, kind, type):
        # definition scoped to class
        if kind in ('STATIC', 'FIELD'):
            self.class_table[name] = (kind, type, self.indices[kind])
        # definition scoped to subroutine
        else:  # 'ARG' or 'VAR'
            self.subroutine_table[name] = (kind, type, self.indices[kind])
        self.indices[kind] += 1

    def var_count(self, kind):
        return self.indices[kind]

    def kind_of(self, name):
        return self.lookup(name)[0]

    def type_of(self, name):
        return self.lookup(name)[1]

    def index_of(self, name):
        return self.lookup(name)[2]

    def lookup(self, name):
        if name in self.subroutine_table:
            return self.subroutine_table[name]
        elif name in self.class_table:
            return self.class_table[name]
        else:
            return 'NONE'
