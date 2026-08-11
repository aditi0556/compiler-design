%{
#include "str_parser.tab.h"
%}

%%
[0-1]     { return yytext[0]; }
\n        { return 0; }
.         { return yytext[0]; }
%%

int yywrap(){ return 1; }
