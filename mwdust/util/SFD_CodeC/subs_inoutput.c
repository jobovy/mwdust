
#include <unistd.h> /* For access() */
#include <string.h>
#include "subs_inoutput.h"

/* Initialize file pointers to NULL -- this is done automatically since
 * this is an external variable.
 * Files are numbered 0 to IO_FOPEN_MAX-1.
 */
FILE  *  pFILEfits[IO_FOPEN_MAX];

/******************************************************************************/
/* Return IO_GOOD if a file exists, and IO_BAD otherwise.
 */
int inoutput_file_exist
  (char  *  pFileName)
{
   int      retval;

   if (access(pFileName, F_OK) == 0) {
      retval = IO_GOOD;
   } else {
      retval = IO_BAD;
   }
   return retval;
}

/******************************************************************************/
/* Return the index number of the first unused (NULL) file pointer.
 * If there are no free file pointers, then return IO_FOPEN_MAX.
 */
int inoutput_free_file_pointer_()
{
   int retval = 0;
 
   while(retval <= IO_FOPEN_MAX && pFILEfits[retval] != NULL) retval++;
   return retval;
}

/******************************************************************************/
/* 
 * Open a file for reading or writing.
 * A file number for the file pointer is returned in *pFilenum.
 *
 * Return IO_GOOD if the file was successfully opened, IO_BAD otherwise.
 * Failure can be due to either lack of free file pointers, or
 * the file not existing if pPriv=="r" for reading.
 */
int inoutput_open_file
  (int   *  pFilenum,
   char     pFileName[],
   char     pPriv[])
{
   int      iChar;
   int      retval;
   char     tempName[IO_FORTRAN_FL];

   if ((*pFilenum = inoutput_free_file_pointer_()) == IO_FOPEN_MAX) {
      printf("ERROR: Too many open files\n");
      retval = IO_BAD;
   } else {
      /* Truncate the Fortran-passed file name with a null,
       * in case it is padded with spaces */
      iChar = IO_FORTRAN_FL;
      strncpy(tempName, pFileName, iChar);
      for (iChar=0; iChar < IO_FORTRAN_FL; iChar++) {
         if (tempName[iChar] == ' ') tempName[iChar] = '\0';
      }

      retval = IO_GOOD;
      if (pPriv[0] == 'r') {
         if (inoutput_file_exist(tempName) == IO_GOOD) {
            if ((pFILEfits[*pFilenum] = fopen(tempName, pPriv)) == NULL) {
               printf("ERROR: Error opening file: %s\n", tempName);
               retval = IO_BAD;
            }
         } else {
            printf("ERROR: File does not exist: %s\n", tempName);
            retval = IO_BAD;
         }
      } else {
         if ((pFILEfits[*pFilenum] = fopen(tempName, pPriv)) == NULL) {
            printf("ERROR: Error opening file: %s\n", tempName);
            retval = IO_BAD;
         }
      }
   }

   return retval;
}

/******************************************************************************/
/*
 * Close a file.  Free the file pointer so it can be reused.
 * Return IO_BAD if an error is encountered; otherwise return IO_GOOD.
 */
int inoutput_close_file
  (int      filenum)
{
   int      retval;

   if (fclose(pFILEfits[filenum]) == EOF) {
      retval = IO_BAD;
   } else {
      retval = IO_GOOD;
   }
   pFILEfits[filenum] = NULL;

   return retval;
}

