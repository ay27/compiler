import g

__author__ = 'ay27'


class Table(object):
    def __init__(self, sym, id):
        self.sym = sym
        self.id = id

    def __repr__(self):
        return self.sym + '\t' + self.id


_TOKEN = ('begin', 'end', 'integer', 'if', 'then',
          'else', 'function', 'read', 'write', 'symbol',
          'const', '=', '<>', '<=', '<',
          '>=', '>', '-', '*', ':=',
          '(', ')', ';', 'EOLN', 'EOF')

KEYWORDS = ('begin', 'end', 'integer', 'if', 'then',
            'else', 'function', 'read', 'write')
OPERATIONS = ('=', '<>', '<=', '<',
              '>=', '>', '-', '*', ':=',
              '(', ')', ';')

BEGIN = 'begin'
END = 'end'
INTEGER = 'integer'
IF = 'if'
THEN = 'then'
ELSE = 'else'
FUNCTION = 'function'
READ = 'read'
WRITE = 'write'
SYMBOL = 'symbol'
CONST = 'const'
EOLN = 'EOLN'
EOF = 'EOF'
EQUAL = '='
NOT_EQUAL = '<>'
LE = '<='
LITTLE = '<'
GE = '>='
GREATER = '>'
SUB = '-'
MUL = '*'
ASSIGN = ':='
LEFT_BRACKET = '('
RIGHT_BRACKET = ')'
SEMICOLON = ';'

TOKEN_TABLE = {}


def init_token_table():
    for symbol, id in zip(_TOKEN, range(1, len(_TOKEN) + 1)):
        TOKEN_TABLE[symbol] = id


