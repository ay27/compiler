from lexer import lex
from io_lib import err, debug
import g
from parser import parse

__author__ = 'ay27'

from table import init_token_table

if __name__ == '__main__':
    try:
        g.pas_src = open(g.src_file_name)
    except OSError:
        err('can not open file %s' % g.src_file_name)
        exit(-1)

    if g.pas_src is None:
        err('can not open file %s' % g.src_file_name)
        exit(-1)

    init_token_table()
    debug('token table init finish')
    try:
        lex(g.pas_src)
    except IOError:
        err('something error')
    debug('lex finish')

    g.dyd = open('test.dyd')
    try:
        parse(g.dyd)
    except StopIteration:
        print('finish')
