# compiler-design

for second qs
bison -d -o str_parser.tab.cpp --defines=str_parser.tab.h str_parser.y
flex -o str_lexer.yy.cpp str_lexer.l
g++ str_lexer.yy.cpp str_parser.tab.cpp -o str -lfl
./str
Enter string: 001
Accepted
