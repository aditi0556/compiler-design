%{
#include <iostream>
#include <cstdlib>
using namespace std;

int yylex();
void yyerror(const char *s);
%}

%token NUMBER PLUS MINUS MUL DIV MOD LPAREN RPAREN
%left PLUS MINUS
%left MUL DIV MOD
%right UMINUS

%%

line
    : expr '\n'   { cout << "Result = " << $1 << endl; exit(0); }
    ;

expr
    : expr PLUS expr          { $$ = $1 + $3; }
    | expr MINUS expr         { $$ = $1 - $3; }
    | expr MUL expr           { $$ = $1 * $3; }
    | expr DIV expr           {
                                   if ($3 == 0) { yyerror("Error: Division by zero"); exit(0); }
                                   $$ = $1 / $3;
                               }
    | expr MOD expr           {
                                   if ($3 == 0) { yyerror("Error: Modulus by zero"); exit(0); }
                                   $$ = $1 % $3;
                               }
    | LPAREN expr RPAREN      { $$ = $2; }
    | MINUS expr %prec UMINUS { $$ = -$2; }
    | NUMBER                  { $$ = $1; }
    ;

%%

void yyerror(const char *s) {
    cout << s << endl;
}

int main() {
    cout << "Enter an arithmetic expression: ";
    yyparse();
    return 0;
}
