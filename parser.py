from io_lib import err, out_var, out_proc, debug
import table

__author__ = 'ay27'

'''
文法                                                                字母表示                          消除左递归等
<程序>→<分程序>                                                      S->T                            删去
<分程序>→begin <说明语句表>；<执行语句表> end                            T->begin H;E end               S-> begin H;E end
<说明语句表>→<说明语句>│<说明语句表> ；<说明语句>                          H->A|H;A                        H->AH'  H'->;AH'|e
<说明语句>→<变量说明>│<函数说明>                                        A->V|F                          A->integer D | integer function D(D);S
<变量说明>→integer <变量>                                             V->integer C                    V->integer D
<变量>→<标识符>                                                      C->D                            删去
<标识符>→<字母>│<标识符><字母>│ <标识符><数字>                           D->G|DG|DN                      D->GD'  D'->GD'|ND'|e
<字母>→a│b│c│d│e│f│g│h│i│j│k│l│m│n│o │p│q │r│s│t│u│v│w│x│y│z        G->a|b|c....
<数字>→0│1│2│3│4│5│6│7│8│9                                          N->0|1|2...
<函数说明>→integer function <标识符>（<参数>）；<函数体>                 F->integer function D(M);S
<参数>→<变量>                                                        M->C
<函数体>→begin <说明语句表>；<执行语句表> end                            S->begin H;E end
<执行语句表>→<执行语句>│<执行语句表>；<执行语句>                           E->B|E;B                        E->BE'  E'->;BE'|e
<执行语句>→<读语句>│<写语句>│<赋值语句>│<条件语句>                         B->R|W|Z|I
<读语句>→read(<变量>)                                                R->read(C)                     R->read(D)
<写语句>→write(<变量>)                                               W->write(C)                    W->write(D)
<赋值语句>→<变量>:=<算术表达式>                                        Z->C:=K                         Z->D:=K
<算术表达式>→<算术表达式>-<项>│<项>                                     K->K-L|L                        K->LK'  K'=-LK'|e
<项>→<项>*<因子>│<因子>                                              L->L*Y|Y                        L->YL'  L'->*YL'|e
<因子>→<变量>│<常数>│<函数调用>                                        Y->C|O|P                       Y->D|Q|P
<常数>→<无符号整数>                                                  O->Q                              删去
<无符号整数>→<数字>│<无符号整数><数字>                                  Q->N|QN                          Q->NQ'  Q'->NQ'|e
<函数调用>→<标识符>（<参数>）                                          P->D(M)
<条件语句>→if<条件表达式>then<执行语句>else <执行语句>                   I->if U then B else B
<条件表达式>→<算术表达式><关系运算符><算术表达式>                         U->KVK
<关系运算符> →<│<=│>│>=│=│<>                                        V-><|<=|...


完整的文法如下：
1. S->begin HE end      更改：去掉分号

2.  H->integer V;H'             更改：添上分号
3.  H'->integer V;H'|e          更改：天上那个分号
# 4.  A->integer V
4.  V->D|function D(M);S
5.  D->GD'
6.  D'->GD'|ND'|e
7.  G->a|b|c....
8.  N->0|1|2...
9. M->D

10. E->BE'
11. E'->;BE'|e
12. B->read(D)|write(D)|if U then B else B|Z
13. Z->D:=K

14. K->LK'
15. K'=-LK'|e
16. L->YL'
17. L'->*YL'|e
18. Y->D|Q|P            更改为：Y->GD'|NQ'|D(M)
19. Q->NQ'
20. Q'->NQ'|e
21. P->D(M)             更改：删去
22. U->KOK
23. O-><|<=|=...


'''


class Variable(object):
    """
        变量名vname: char(16)
        所属过程vproc:char(16)
        分类vkind: 0..1(0—变量、1—形参)
        变量类型vtype: types
        变量层次vlev: int
        变量在变量表中的位置vadr: int(相对第一个变量而言)
        types=(ints)
    """

    def __init__(self, vname, vproc, vkind, vtype, vlen, vadr):
        self.vname = vname
        self.vproc = vproc
        self.vkind = vkind
        self.vtype = vtype
        self.vlen = vlen
        self.vadr = vadr

    def __repr__(self):
        return '%s %s %d %s %d %d' % (self.vname, self.vproc, self.vkind, self.vtype, self.vlen, self.vadr)


class Proc(object):
    """
        过程名pname: char(16)
        过程类型ptype: types
        过程层次plev: int
        第一个变量在变量表中的位置fadr: int
        最后一个变量在变量表中的位置ladr: int
    """

    def __init__(self, pname, ptype, plev):
        self.pname = pname
        self.ptype = ptype
        self.plev = plev
        self.fadr = -1
        self.ladr = -1
        self.adr = len(proc_table)

    def __repr__(self):
        return '%s %s %d %d %d' % (self.pname, self.ptype, self.plev, self.fadr, self.ladr)


var_table = []
proc_table = []
plevel = 0
current_proc = None
current_token = None
current_const = None
line_no = 1


def is_var_exist(token, proc, kind, expected=False):
    """
    在以下场合需要验证变量是否存在：
            1. 引入变量时需要检查是否已定义
            2. 赋值语句的左半部分 Z
            3. 因子表达式    Y

    :param token:
    :param expected: 期望值
    :return:
    """
    for t in var_table:
        if t.vname == token and t.vproc == proc and t.vkind == kind:
            if not expected:
                return False
                # err('CheckVarExist : expected=False, but now is True  %s' % token)
            else:
                return True
    if expected:
        return False
        # err('CheckVarExist : expected=True, but now is False  %s' % token)
    return False


def add_var(token, proc, kind, type, vlev):
    """
        只有两个地方会引入新变量：
            1. 变量定义和函数定义 V
            2. read   B
    :param token:
    :param proc:
    :param kind: 分类vkind: 0..1(0—变量、1—形参)
    :param type:
    :param vlev:
    :return:
    """
    if is_var_exist(token, proc=proc, kind=kind, expected=False):
        err('In line %d    AddVar : can not define a variable in twice' % line_no)
    var_table.append(Variable(token, proc, kind, type, vlev, len(var_table)))
    for i in range(0, proc.plev):
        if proc_table[i].plev < vlev or (proc_table[i].plev == vlev and proc_table[i].adr == proc.adr):
            proc_table[i].ladr += 1


def next_token(dyd_file):
    rep = None
    global line_no
    for line in dyd_file:
        debug(line)
        if line is not None and len(line) > 0:
            tmp = line.split()
            if tmp == table.EOF:
                return
            elif tmp is not None and tmp[0] == table.EOLN:
                line_no += 1
                continue
            elif len(tmp) == 2 and tmp[0]:
                while rep is not None and rep:
                    rep = yield tmp[0], tmp[1]
                else:
                    rep = yield tmp[0], tmp[1]


def match(token, token_id, keyword):
    if token is None:
        return False
    # 标识符
    if keyword == table.SYMBOL and token[0].isalpha() and token.isalnum():
        return True
    # 数字
    if keyword == table.CONST and token.isnumeric():
        return True
    # 关键词
    if keyword == token:
        return True
    # 关系运算符类
    if keyword is None and (token == table.EQUAL or token == table.NOT_EQUAL or token == table.LE or
                                    token == table.LITTLE or token == table.GE or token == table.GREATER):
        return True
    return False


def parse(dyd_file):
    S(next_token(dyd_file), 'main', 'void')

    for var in var_table:
        out_var(var.vname, var.vproc, var.vkind, var.vtype, var.vlen, var.vadr)
    # 计算每个proc的fadr和ladr，然后输出
    for proc in proc_table:
        for i in range(0, len(var_table) - 1):
            if var_table[i].vproc.adr == proc.adr:
                proc.fadr = i
                break
        for i in range(len(var_table) - 1, 0, -1):
            if var_table[i].vproc.adr == proc.adr:
                proc.ladr = i
                break

        out_proc(proc.pname, proc.ptype, proc.plev, proc.fadr, proc.ladr)


# 1. S->begin HE end
def S(token_generator, pname, ptype):
    global plevel, current_proc
    plevel += 1
    # 注意到函数有且仅有一个参数，而刚进入函数体时，变量表中的最后一个必为此参数
    if len(var_table) == 0:
        current_proc = Proc(pname, ptype, plevel)
    else:
        current_proc = Proc(pname, ptype, plevel)
        var_table[len(var_table) - 1].vproc = current_proc
    proc_table.append(current_proc)
    # 同时，由于在函数内可以直接把自身函数名当成一个变量来使用，所以需要把函数名加入到变量表
    add_var(pname, current_proc, 0, 'integer', plevel)

    token, token_id = next(token_generator)
    if not match(token, token_id, table.BEGIN):
        err('In line %d    S : Not start with begin' % line_no)
    H(token_generator)
    # token, token_id = next(token_generator)
    # if not match(token, token_id, table.SEMICOLON):
    # err('S : A ; must follow H')
    E(token_generator)
    token, token_id = next(token_generator)
    if not match(token, token_id, table.END):
        err('In Line %d    S : there must be an \'end\'' % line_no)

    plevel -= 1
    current_proc = proc_table[plevel - 1]
    return


# 2. H->integer V;H'
def H(token_generator):
    token, token_id = next(token_generator)
    if not match(token, token_id, table.INTEGER):
        err('In Line %d   H : can not match integer' % line_no)
    V(token_generator)
    token, token_id = next(token_generator)
    if not match(token, token_id, table.SEMICOLON):
        err('In Line %d   H : can not match ;' % line_no)
    _H(token_generator)
    return


# 3. H'->integer V;H'|e
def _H(token_generator):
    token, token_id = token_generator.send(True)
    # 没有匹配成功，可能是e，需要回退一步
    if not match(token, token_id, table.INTEGER):
        return
    # 匹配integer成功，需要把重复的这个yield冲刷掉
    next(token_generator)
    V(token_generator)
    token, token_id = next(token_generator)
    if not match(token, token_id, table.SEMICOLON):
        err('In Line %d    H : can not match ;' % line_no)
    _H(token_generator)


# # 4.  A->integer V
# def A(token_generator):
# token, token_id = next(token_generator)
# if not match(token, token_id, table.INTEGER):
# err('A : can not match integer')
# V(token_generator)


# 5.  V->D|function D(M);S
def V(token_generator):
    token, token_id = token_generator.send(True)
    if not match(token, token_id, table.FUNCTION):
        D(token_generator)
        add_var(current_token, current_proc, 0, 'integer', plevel)
        return
    # 冲刷掉当前token
    next(token_generator)
    D(token_generator)
    func_name = current_token
    token, token_id = next(token_generator)
    if not match(token, token_id, table.LEFT_BRACKET):
        err('In line %d    V : can not match (' % line_no)
    M(token_generator)
    # 由于current_proc尚未生成，先赋值为当前proc，在进入函数时需要重新设置
    add_var(current_token, current_proc, 1, 'integer', plevel + 1)

    token, token_id = next(token_generator)
    if not match(token, token_id, table.RIGHT_BRACKET):
        err('In Line %d    V : can not match )' % line_no)
    token, token_id = next(token_generator)
    if not match(token, token_id, table.SEMICOLON):
        err('In Line %d    V : can not match ;' % line_no)

    S(token_generator, func_name, 'integer')


# 6.  D->GD'
def D(token_generator):
    if not G(token_generator):
        err('In Line %d    D : match %s error' % (line_no, current_token))
    _D(token_generator)
    return


# 7.  D'->GD'|ND'|e
def _D(token_generator):
    if G(token_generator):
        _D(token_generator)
    elif N(token_generator):
        _D(token_generator)
    else:
        return


# 8.  G->a|b|c....
def G(token_generator):
    token, token_id = token_generator.send(True)
    if match(token, token_id, table.SYMBOL):
        next(token_generator)
        global current_token
        current_token = token
        return True
    return False


# 9.  N->0|1|2...
def N(token_generator):
    token, token_id = token_generator.send(True)
    if match(token, token_id, table.CONST):
        next(token_generator)
        global current_const
        current_const = token
        return True
    return False


# 10. M->D
def M(token_generator):
    D(token_generator)


# 11. E->BE'
def E(token_generator):
    B(token_generator)
    _E(token_generator)
    return


# 12. E'->;BE'|e
def _E(token_generator):
    token, token_id = token_generator.send(True)
    if not match(token, token_id, table.SEMICOLON):
        return
    next(token_generator)
    B(token_generator)
    _E(token_generator)


# 13. B->read(D)|write(D)|if U then B else B|Z
def B(token_generator):
    token, token_id = token_generator.send(True)
    # func_is_read = match(token, token_id, table.READ)
    if match(token, token_id, table.READ) or match(token, token_id, table.WRITE):
        # 成功，冲刷
        next(token_generator)
        token, token_id = next(token_generator)
        if not match(token, token_id, table.LEFT_BRACKET):
            err('In Line %d    B : can not match (' % line_no)
        D(token_generator)
        if not is_var_exist(current_token, current_proc, 0, True):
            err('In Line %d    B : can not find token %s' % (line_no, current_token))
        # if func_is_read:
        # add_var(current_token, current_proc, 0, 'integer', plevel)

        token, token_id = next(token_generator)
        if not match(token, token_id, table.RIGHT_BRACKET):
            err('In Line %d    B : can not match )' % line_no)
    elif match(token, token_id, table.IF):
        # 成功，冲刷
        next(token_generator)
        U(token_generator)
        token, token_id = next(token_generator)
        if not match(token, token_id, table.THEN):
            err('In Line %d    B : can not match then' % line_no)
        B(token_generator)
        token, token_id = next(token_generator)
        if not match(token, token_id, table.ELSE):
            err('In Line %d    B : can not match else' % line_no)
        B(token_generator)
    else:
        Z(token_generator)


# 14. Z->D:=K
def Z(token_generator):
    D(token_generator)
    if not is_var_exist(current_token, current_proc, 0, True):
        err('In Line %d     Z : token %s not defined' % (line_no, current_token))
    token, token_id = next(token_generator)
    if not match(token, token_id, table.ASSIGN):
        err('In Line %d    Z : can not match := %s' % (line_no, token))
    K(token_generator)


# 15. K->LK'
def K(token_generator):
    L(token_generator)
    _K(token_generator)


# 16. K'=-LK'|e
def _K(token_generator):
    token, token_id = token_generator.send(True)
    if not match(token, token_id, table.SUB):
        return
    # 冲刷
    next(token_generator)
    L(token_generator)
    _K(token_generator)


# 17. L->YL'
def L(token_generator):
    Y(token_generator)
    _L(token_generator)


# 18. L'->*YL'|e
def _L(token_generator):
    token, token_id = token_generator.send(True)
    if not match(token, token_id, table.MUL):
        return
    # 冲刷
    next(token_generator)
    Y(token_generator)
    _L(token_generator)


# 19. Y->NQ'|GD'|D(M)
# 其中，D == GD'
def Y(token_generator):
    # 先检查是否是数字
    if N(token_generator):
        _Q(token_generator)
        return

    # 然后检查是否是函数调用
    D(token_generator)
    func_name = current_token
    token, token_id = token_generator.send(True)
    if not match(token, token_id, table.LEFT_BRACKET):
        # 不是函数调用
        if not is_var_exist(current_token, current_proc, 0, True):
            err('In Line %d    Y : %s is not defined' % (line_no, current_token))
        _D(token_generator)
        return

    # 确实是函数
    # 检查函数是否已定义
    flag = False
    for proc in proc_table:
        if proc.pname == func_name:
            flag = True
            break
    if not flag:
        err('In Line %d    P : function not defined' % line_no)
    # 冲刷
    next(token_generator)
    K(token_generator)
    token, token_id = next(token_generator)
    if not match(token, token_id, table.RIGHT_BRACKET):
        err('In Line %d    P : can not match )' % line_no)


# 20. Q->NQ'
def Q(token_generator):
    if not N(token_generator):
        err('In Line %d    Q : match number error %s' % (line_no, current_token))
    _Q(token_generator)


# 21. Q'->NQ'|e
def _Q(token_generator):
    if N(token_generator):
        _Q(token_generator)
    else:
        return


# 23. U->KOK
def U(token_generator):
    K(token_generator)
    O(token_generator)
    K(token_generator)


# 24. O-><|<=|=...
def O(token_generator):
    token, token_id = next(token_generator)
    if not match(token, token_id, None):
        err('In Line %d    O : can not match %s' % (line_no, token))


