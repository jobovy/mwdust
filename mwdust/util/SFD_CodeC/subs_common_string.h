
#ifndef __INCsubs_common_string_h
#define __INCsubs_common_string_h

#include <stdio.h> /* Include for definition of FILE */

//Removed because it conflicts with stdio.h
//int getline
//  (char  *  pLine,
//   int      max);
float sexagesimal_to_float
  (char  *  pTimeString);
void trim_string
  (char  *  pName,
   int      nChar);
char * get_next_line
  (char  *  pNextLine,
   int      maxLen,
   FILE  *  pFILE);
void string_to_integer_list
  (char  *  pString,
   int   *  pNEntry,
   int   ** ppEntry);

#endif /* __INCsubs_common_string_h */
