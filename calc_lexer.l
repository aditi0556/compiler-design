%{
#include "calc_parser.tab.h"
%}

%%
[0-9]+      { yylval = atoi(yytext); return NUMBER; }
[ \t]       ;
\n          { return yytext[0]; }
"+"         { return PLUS; }
"-"         { return MINUS; }
"*"         { return MUL; }
"/"         { return DIV; }
"%"         { return MOD; }
"("         { return LPAREN; }
")"         { return RPAREN; }
.           { return yytext[0]; }
%%

int yywrap(){ return 1; }

