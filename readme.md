#README
一个简单的词法分析器和语法分析器。

```bash
.
├── g.py
├── io_lib.py
├── lexer.py
├── main.py
├── parser.py
├── table.py
├── test.dyd
├── test.err
├── test.pas
├── test.pro
└── test.var
```

lexer是词法分析器，parser是语法分析器。需要分析的源文件是pascal语言编写的简单代码。

lexer将源文件（test.pas）完成词法分析后输出一个dyd文件，parser利用dyd文件完成语法分析，得到var和pro两个文件，var是代码的变量表，pro是代码的区块表。

完整的文法如下：

```
1.  S->begin HE end
2.  H->integer V;H'
3.  H'->integer V;H'|e
4.  V->D|function D(M);S
5.  D->GD'
6.  D'->GD'|ND'|e
7.  G->a|b|c....
8.  N->0|1|2...
9.  M->D
10. E->BE'
11. E'->;BE'|e
12. B->read(D)|write(D)|if U then B else B|Z
13. Z->D:=K
14. K->LK'
15. K'=-LK'|e
16. L->YL'
17. L'->*YL'|e
18. Y->GD'|NQ'|D(M)
19. Q->NQ'
20. Q'->NQ'|e
21. U->KOK
22. O-><|<=|=...

```