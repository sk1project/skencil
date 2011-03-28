#define WHITESPACE 0x0001
#define NEWLINE 0x0002
#define DELIMITER 0x0004
#define COMMENT 0x0008
#define DIGIT 0x0010
#define INTCHAR 0x0020
#define FLOATCHAR 0x0040
#define NAMECHAR 0x0100
static int char_types[] = {
0x001, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\000' .. '\007' */
0x100, 0x001, 0x003, 0x100, 0x003, 0x003, 0x100, 0x100, /* '\010' .. '\017' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\020' .. '\027' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\030' .. '\037' */
0x001, 0x100, 0x100, 0x100, 0x100, 0x008, 0x100, 0x100, /* ' ' .. '\'' */
0x004, 0x004, 0x100, 0x160, 0x100, 0x160, 0x140, 0x004, /* '(' .. '/' */
0x170, 0x170, 0x170, 0x170, 0x170, 0x170, 0x170, 0x170, /* '0' .. '7' */
0x170, 0x170, 0x100, 0x100, 0x004, 0x100, 0x004, 0x100, /* '8' .. '?' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x140, 0x100, 0x100, /* '@' .. 'G' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* 'H' .. 'O' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* 'P' .. 'W' */
0x100, 0x100, 0x100, 0x004, 0x100, 0x004, 0x100, 0x100, /* 'X' .. '_' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x140, 0x100, 0x100, /* '`' .. 'g' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* 'h' .. 'o' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* 'p' .. 'w' */
0x100, 0x100, 0x100, 0x004, 0x100, 0x004, 0x100, 0x100, /* 'x' .. '' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\200' .. '\207' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\210' .. '\217' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\220' .. '\227' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '\230' .. '\237' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, 0x100, /* '�' .. '�' */
};
