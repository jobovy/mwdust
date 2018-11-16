
#ifndef __INCsubs_inoutput_h
#define __INCsubs_inoutput_h

#include <stdio.h> /* Include for definition of FILE */

#define MAX_FILE_LINE_LEN 500 /* Maximum line length for data files */
#define MAX_FILE_NAME_LEN  80
#define IO_FOPEN_MAX       20  /* Files must be numbered 0 to IO_FOPEN_MAX-1 */
#define IO_FORTRAN_FL     120  /* Max length of file name from a Fortran call */
#define IO_GOOD             1
#define IO_BAD              0

extern FILE  *  pFILEfits[];

int inoutput_file_exist
  (char  *  pFileName);
int inoutput_free_file_pointer_();
int inoutput_open_file
  (int   *  pFilenum,
   char     pFileName[],
   char     pPriv[]);
int inoutput_close_file
  (int      filenum);

#endif /* __INCsubs_inoutput_h */
