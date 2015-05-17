import g

__author__ = 'ay27'


def err(err_str):
    if g.err is None:
        g.err = open('test.err', mode='w')
    g.err.write('%s\n' % err_str)
    print('ERROR: %s\n' % err_str)
    exit(-1)


def debug(dbg_str):
    print('DEBUG: %s\n' % dbg_str)


def out_dyd(token, id):
    if g.dyd is None:
        g.dyd = open('test.dyd', mode='w')
    g.dyd.write('%-16s %2d\n' % (token, id))
    debug('%-16s %2d\n' % (token, id))


def out_var(vname, vproc, vkind, vtype, vlen, vadr):
    if g.var is None:
        g.var = open('test.var', mode='w')
        g.var.write('vname    vproc    vkind    vtype    vlev    vadr\n')
    out_str = '%-8s %-8s %-8d %-8s %-8d %-8d\n' % (vname, vproc.adr, vkind, vtype, vlen, vadr)
    g.var.write(out_str)
    debug(out_str)

def out_proc(pname, ptype, plev, fadr, ladr):
    if g.proc is None:
        g.proc = open('test.pro', mode='w')
    out_str = '%s %s %d %d %d\n' % (pname, ptype, plev, fadr, ladr)
    g.proc.write(out_str)
    debug(out_str)