%{
#include <iostream>
using namespace std;

int yylex();
void yyerror(const char *s);
%}

%%

S
    : '0' S
    | '0' '1'
    ;

%%

void yyerror(const char *s) {
    /* silent - result checked via yyparse() return value */
}

int main() {
    cout << "Enter string: ";
    if (yyparse() == 0)
        cout << "Accepted" << endl;
    else
        cout << "Rejected" << endl;
    return 0;
}
