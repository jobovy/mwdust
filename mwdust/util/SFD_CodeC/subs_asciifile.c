
#include <stdio.h>
#include <string.h>
#include "subs_memory.h"
#include "subs_inoutput.h"
#include "subs_asciifile.h"

/******************************************************************************/
/*
 * Read an ASCII file as a 2-dimensional array of floating point numbers.
 * The number of columns is determined by the number of entries on the
 * first non-comment line.  Missing values are set to zero.
 * Comment lines (preceded with a hash mark) are ignored.
 * The returned matrix is in COLUMN-MAJOR order, and as such is
 * addressed as (*ppData)[iCol*NRows+iRow].
 * This is the Fortran storage scheme, but it is useful in addressing
 * a column as a vector that is contiguous in memory.
 * If the data array is empty, it should be passed with the value ppData = NULL.
 *
 * Return IO_GOOD if the file exists, and IO_FALSE otherwise.
 */
int asciifile_read_colmajor
  (char     pFileName[],
   int      numColsMax,
   int   *  pNRows,
   int   *  pNCols,
   float ** ppData)
{
   int      iCol;
   int      iRow;
   int      qExist;
   MEMSZ    memSize;
   float *  pNewData;

   qExist = asciifile_read_rowmajor(pFileName, numColsMax,
    pNRows, pNCols, ppData);

   if (qExist == IO_GOOD) {
      /* Create a new array of the same dimensions */
      memSize = sizeof(float) * (*pNRows)*(*pNCols);
      ccalloc_(&memSize, (void **)&pNewData);

      /* Copy the data into this array in column-major order */
      for (iCol=0; iCol < (*pNCols); iCol++) {
      for (iRow=0; iRow < (*pNRows); iRow ++) {
         pNewData[iCol*(*pNRows)+iRow] = (*ppData)[iRow*(*pNCols)+iCol];
      } }

      /* Toss out the old array */
      ccfree_((void **)ppData);
      *ppData = pNewData;
   }

   return qExist;
}

/******************************************************************************/
/*
 * Read an ASCII file as a 2-dimensional array of floating point numbers.
 * The number of columns is determined by the number of entries on the
 * first non-comment line.  Missing values are set to zero.
 * Comment lines (preceded with a hash mark) are ignored.
 * The returned matrix is in row-major order, and as such is
 * addressed as (*ppData)[iRow*NCols+iCol].
 * If the data array is empty, it should be passed with the value ppData = NULL.
 *
 * Return IO_GOOD if the file exists, and IO_BAD otherwise.
 */
int asciifile_read_rowmajor
  (char     pFileName[],
   int      numColsMax,
   int   *  pNRows,
   int   *  pNCols,
   float ** ppData)
{
   int      fileNum;
   int      iCol;
   int      nValues;
   int      qExist;
   const int numAddRows = 10;
   MEMSZ    memSize;
   MEMSZ    newMemSize;
   char  *  iq;
   float *  pValues;
   float *  pData;
   char     pPrivR[] = "r\0";

   *pNCols = 0;
   *pNRows = 0;

   qExist = inoutput_open_file(&fileNum, pFileName, pPrivR);

   if (qExist == IO_GOOD) {

      /* Allocate a starting block of memory for the data array */
      /* Start with enough memory for numAddRows rows */
      memSize = numAddRows * sizeof(float) * numColsMax;
      /* SHOULD BE ABLE TO USE REALLOC BELOW !!!??? */
      ccalloc_(&memSize, (void **)ppData);
      pData = *ppData;

      /* Allocate the temporary memory for each line of values */
      pValues = ccvector_build_(numColsMax);

      /* Read the first line, which determines the # of cols for all lines */
      iq = asciifile_read_line(fileNum, numColsMax, pNCols, pData);

      /* Read the remaining lines if a first line was read successfully */
      if (iq != NULL) {
         *pNRows=1;

         while ((iq = asciifile_read_line(fileNum, numColsMax,
          &nValues, pValues)) != NULL) {

            /* Allocate more memory for the data array if necessary */
            /* Always keep enough memory for at least one more row */
            newMemSize = sizeof(float) * (*pNRows + 1) * (*pNCols);
            if (newMemSize > memSize) {
               newMemSize = newMemSize + sizeof(float)*(numAddRows);
               ccalloc_resize_(&memSize, &newMemSize, (void **)ppData);
               pData = *ppData;
               memSize = newMemSize;
            }
   
            /* Case where the line contained fewer values than allowed */
            if (nValues < *pNCols) {
               for (iCol=0; iCol<nValues; iCol++)
                  pData[iCol+(*pNCols)*(*pNRows)] = pValues[iCol];
               for (iCol=nValues; iCol < *pNCols; iCol++)
                  pData[iCol+(*pNCols)*(*pNRows)] = 0;

            /* Case where line contained as many or more values than allowed */
            } else {
               for (iCol=0; iCol < *pNCols; iCol++)
                  pData[iCol+(*pNCols)*(*pNRows)] = pValues[iCol];
            }

            (*pNRows)++;
         }
      }

      inoutput_close_file(fileNum);
      ccvector_free_(pValues);
   }

   return qExist;
}

/******************************************************************************/
/*
 * Read all values from the next line of the input file.
 * Return NULL if end of file is reached.
 * Comment lines (preceded with a hash mark) are ignored.
 */
char * asciifile_read_line
  (int      filenum,
   int      numColsMax,
   int   *  pNValues,
   float *  pValues)
{
   char  *  pRetval;
   const    char whitespace[] = " \t\n";
   char     pTemp[MAX_FILE_LINE_LEN];
   char  *  pToken;

   /* Read next line from open file into temporary string */
   /* Ignore comment lines that are preceded with a hash mark */
   while (( (pRetval = fgets(pTemp, MAX_FILE_LINE_LEN, pFILEfits[filenum]))
    != NULL) && (pTemp[0] == '#') );

   if (pRetval != NULL) {
      /* Read one token at a time as a floating point value */
      *pNValues = 0;
      pToken = pTemp;
      while ((pToken = strtok(pToken, whitespace)) != NULL &&
             (*pNValues) < numColsMax ) {
         sscanf(pToken, "%f", &pValues[*pNValues]);
         pToken = NULL;
         (*pNValues)++;
      }
   }

   return pRetval;
}

