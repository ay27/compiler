from io_lib import out_dyd, debug, err
import table

__author__ = 'ay27'


def parse_token(token):
    if table.TOKEN_TABLE.get(token, -1) != -1:
        return table.TOKEN_TABLE.get(token)
    # check for symbol
    if token[0].isalpha():
        return table.TOKEN_TABLE.get('symbol')
    # check for const
    if token.isnumeric():
        return table.TOKEN_TABLE.get('const')
    return 0


def is_operation(token):
    if token is None or len(token) == 0:
        return False
    for operation in table.OPERATIONS:
        if token == operation:
            return True
    return False


def is_word_end(token, ch):
    if token is None or len(token) == 0:
        return False
    if token.isalnum() and not ch.isalnum():
        return True
    return False


def is_operation_end(token, ch):
    if token is None or len(token) == 0:
        return False
    if is_operation(token) and not is_operation(ch):
        return True
    return False


def get_next_token(src_file):
    for line in src_file:
        token = ''
        for ch in line:
            if ch == ' ' or ch == '\t' or ch == '\r' or ch == '\n':
                if token is not None and len(token) > 0:
                    out_dyd(token, parse_token(token))
                    yield token
                token = ''
            elif token == '' and ch.isdigit():
                err('must not be number start')
            # 三种情况，一个是单词结束，一个是算符结束，一个是两个算符并排，如);
            elif is_word_end(token, ch) or is_operation_end(token, ch) or \
                    (is_operation(token) and is_operation(ch) and not is_operation('%s%s' % (token, ch))):
                out_dyd(token, parse_token(token))
                yield token
                token = ch
            else:
                token += ch
        out_dyd(table.EOLN, table.TOKEN_TABLE.get(table.EOLN))
        # yield table.EOLN
    out_dyd(table.EOF, table.TOKEN_TABLE.get(table.EOF))
    debug('finish')
    # exit(0)
    # yield table.EOF


def lex(src_file):
    token_generator = get_next_token(src_file)
    try:
        while True:
            next(token_generator)
    except StopIteration:
        return
