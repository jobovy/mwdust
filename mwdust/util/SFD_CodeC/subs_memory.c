
#include <stdio.h>
#include <string.h>
#include <stdlib.h> /* Library for malloc(), realloc() and free() */
#include "subs_memory.h"

#ifdef OLD_SUNCC
/******************************************************************************/
/*
 * Copy one section of memory (a string) to another, even if they overlap.
 * The advertised C library routine by this name does not actually exist
 * in old SunOS.
 */
void memmove
  (void  *  s,
   const void  *  ct,
   MEMSZ    n)
{
   MEMSZ    i;
   char  *  ps = (char *)s;
   const char  *  pct = (const char *)ct;
 
   /* Do nothing if ps == pct */
   if (ps > pct) for (i=0; i < n; i++) *(ps+n-i-1) = *(pct+n-i-1);
   else if (ps < pct) for (i=0; i < n; i++) *(ps+i) = *(pct+i);
}
#endif

/******************************************************************************/
/*
 * Change the size of memory for data, and return the new address as *ppData.
 * Copy contents of memory in common.
 */
void ccalloc_resize_
  (MEMSZ *  pOldMemSize,
   MEMSZ *  pNewMemSize,
   void  ** ppData)
{
   void  *  pNewData;

   if (*pNewMemSize > *pOldMemSize) {
      ccalloc_(pNewMemSize,&pNewData);
      memmove((void *)pNewData,(void *)(*ppData),*pOldMemSize);
      ccfree_(ppData);
      *ppData = pNewData;
   } else if (*pNewMemSize < *pOldMemSize) {
      ccalloc_(pNewMemSize,&pNewData);
      memmove((void *)pNewData,(void *)(*ppData),*pNewMemSize);
      ccfree_(ppData);
      *ppData = pNewData;
   }
}

/******************************************************************************/
/*
 * Allocate *pMemSize bytes of data.  The starting memory location is *ppData.
 * If the array has previously been allocated, then resize it.
 */
void ccrealloc_
  (MEMSZ *  pMemSize,
   void  ** ppData)
{
   if (*ppData == NULL) {
      *ppData = (void *)malloc((size_t)(*pMemSize));
   } else {
      *ppData = (void *)realloc(*ppData,(size_t)(*pMemSize));
   }
}

/******************************************************************************/
/*
 * Allocate *pMemSize bytes of data.  The starting memory location is *ppData.
 * Also zero all of the data byes.
 */
void ccalloc_init
  (MEMSZ *  pMemSize,
   void  ** ppData)
{
   size_t   nobj = 1;
   *ppData = (void *)calloc(nobj, (size_t)(*pMemSize));
}

/******************************************************************************/
/*
 * Allocate *pMemSize bytes of data.  The starting memory location is *ppData.
 */
void ccalloc_
  (MEMSZ *  pMemSize,
   void  ** ppData)
{
   *ppData = (void *)malloc((size_t)(*pMemSize));
}

/******************************************************************************/
/*
 * Free the memory block that starts at address *ppData.
 */
void ccfree_
  (void  ** ppData)
{
   free(*ppData);
   *ppData = NULL;
}

/******************************************************************************/
float * ccvector_build_
  (MEMSZ    n)
{
   float * pVector = (float *)malloc((size_t)(sizeof(float) * n));
   return pVector;
}

/******************************************************************************/
double * ccdvector_build_
  (MEMSZ    n)
{
   double * pVector = (double *)malloc((size_t)(sizeof(double) * n));
   return pVector;
}

/******************************************************************************/
int * ccivector_build_
  (MEMSZ    n)
{
   int * pVector = (int *)malloc((size_t)(sizeof(int) * n));
   return pVector;
}
 
/******************************************************************************/
float ** ccpvector_build_
  (MEMSZ    n)
{
   float ** ppVector = (float **)malloc((size_t)(sizeof(float *) * n));
   return ppVector;
}
 
/******************************************************************************/
/* Build a vector of pointers to arrays of type (float **) */
float *** ccppvector_build_
  (MEMSZ    n)
{
   float *** pppVector = (float ***)malloc((size_t)(sizeof(float **) * n));
   return pppVector;
}
 
/******************************************************************************/
float * ccvector_rebuild_
  (MEMSZ    n,
   float *  pOldVector)
{
   float * pVector;

   if (pOldVector == NULL) {
      pVector = (float *)malloc((size_t)(sizeof(float) * n));
   } else {
      pVector = (float *)realloc(pOldVector,(size_t)(sizeof(float) * n));
   }

   return pVector;
}

/******************************************************************************/
double * ccdvector_rebuild_
  (MEMSZ    n,
   double *  pOldVector)
{
   double * pVector;

   if (pOldVector == NULL) {
      pVector = (double *)malloc((size_t)(sizeof(double) * n));
   } else {
      pVector = (double *)realloc(pOldVector,(size_t)(sizeof(double) * n));
   }

   return pVector;
}

/******************************************************************************/
int * ccivector_rebuild_
  (MEMSZ    n,
   int   *  pOldVector)
{
   int   *  pVector;

   if (pOldVector == NULL) {
      pVector = (int *)malloc((size_t)(sizeof(int) * n));
   } else {
      pVector = (int *)realloc(pOldVector,(size_t)(sizeof(int) * n));
   }

   return pVector;
}

/******************************************************************************/
float ** ccpvector_rebuild_
  (MEMSZ    n,
   float ** ppOldVector)
{
   float ** ppVector;

   if (ppOldVector == NULL) {
      ppVector = (float **)malloc((size_t)(sizeof(float *) * n));
   } else {
      ppVector = (float **)realloc(ppOldVector,(size_t)(sizeof(float *) * n));
   }

   return ppVector;
}

/******************************************************************************/
/* Build a vector of pointers to arrays of type (float **) */
float *** ccppvector_rebuild_
  (MEMSZ    n,
   float *** pppOldVector)
{
   float *** pppVector;
 
   if (pppOldVector == NULL) {
      pppVector = (float ***)malloc((size_t)(sizeof(float **) * n));
   } else {
      pppVector = (float ***)realloc(pppOldVector,(size_t)(sizeof(float **) * n)
);
   }
 
   return pppVector;
}

/******************************************************************************/
void ccvector_free_
  (float *  pVector)
{
   free((void *)pVector);
}

/******************************************************************************/
void ccdvector_free_
  (double *  pVector)
{
   free((void *)pVector);
}

/******************************************************************************/
void ccivector_free_
  (int   *  pVector)
{
   free((void *)pVector);
}

/******************************************************************************/
void ccpvector_free_
  (float ** ppVector)
{
   free((void *)ppVector);
}

/******************************************************************************/
void ccppvector_free_
  (float *** pppVector)
{
   free((void *)pppVector);
}

/******************************************************************************/
/* Build an nRow x nCol matrix, in pointer-style.
 * Allocate one contiguous array of floats with  nRow*nCol elements.
 * Then create a set of nRow pointers, each of which points to the next nCol
 *  elements.
 */
float ** ccarray_build_
  (MEMSZ    nRow,
   MEMSZ    nCol)
{
   MEMSZ    iRow;
 
   float *  pSpace  = (float *)malloc(sizeof(float ) * nRow * nCol);
   float ** ppArray = (float**)malloc(sizeof(float*) * nRow);

   for (iRow = 0; iRow < nRow; iRow++) {
      /* Quantity (iRow*nCol) scales by sizeof(float) */
      ppArray[iRow] = pSpace + (iRow * nCol);
   }

   return ppArray;
}

/******************************************************************************/
/* Build an nRow x nCol matrix, in pointer-style.
 * Allocate one contiguous array of doubles with  nRow*nCol elements.
 * Then create a set of nRow pointers, each of which points to the next nCol
 *  elements.
 */
double ** ccdarray_build_
  (MEMSZ    nRow,
   MEMSZ    nCol)
{
   MEMSZ    iRow;
 
   double *  pSpace  = (double *)malloc(sizeof(double ) * nRow * nCol);
   double ** ppArray = (double**)malloc(sizeof(double*) * nRow);

   for (iRow = 0; iRow < nRow; iRow++) {
      /* Quantity (iRow*nCol) scales by sizeof(double) */
      ppArray[iRow] = pSpace + (iRow * nCol);
   }

   return ppArray;
}

/******************************************************************************/
/* Build an nRow x nCol matrix, in pointer-style.
 * Allocate one contiguous array of ints with  nRow*nCol elements.
 * Then create a set of nRow pointers, each of which points to the next nCol
 *  elements.
 */
int ** cciarray_build_
  (MEMSZ    nRow,
   MEMSZ    nCol)
{
   MEMSZ    iRow;
 
   int *  pSpace  = (int *)malloc(sizeof(int ) * nRow * nCol);
   int ** ppArray = (int**)malloc(sizeof(int*) * nRow);

   for (iRow = 0; iRow < nRow; iRow++) {
      /* Quantity (iRow*nCol) scales by sizeof(int) */
      ppArray[iRow] = pSpace + (iRow * nCol);
   }

   return ppArray;
}

/******************************************************************************/
/* Build an nRow x nCol matrix, in pointer-style.
 * Allocate one contiguous array of floats with  nRow*nCol elements.
 * Then create a set of nRow pointers, each of which points to the next nCol
 *  elements.
 */
float ** ccarray_rebuild_
  (MEMSZ    nRow,
   MEMSZ    nCol,
   float ** ppOldArray)
{
   MEMSZ    iRow;
 
   float *  pSpace;
   float ** ppArray;

   if (ppOldArray == NULL) {
      pSpace  = (float *)malloc(sizeof(float ) * nRow * nCol);
      ppArray = (float**)malloc(sizeof(float*) * nRow);
   } else {
      ppArray = (float**)realloc(ppOldArray, sizeof(float*) * nRow);
      pSpace  = (float *)realloc(ppOldArray[0],sizeof(float ) * nRow * nCol);
   }

   for (iRow = 0; iRow < nRow; iRow++) {
      /* Quantity (iRow*nCol) scales by sizeof(float) */
      ppArray[iRow] = pSpace + (iRow * nCol);
   }

   return ppArray;
}

/******************************************************************************/
/* Build an nRow x nCol matrix, in pointer-style.
 * Allocate one contiguous array of doubles with  nRow*nCol elements.
 * Then create a set of nRow pointers, each of which points to the next nCol
 *  elements.
 */
double ** ccdarray_rebuild_
  (MEMSZ    nRow,
   MEMSZ    nCol,
   double ** ppOldArray)
{
   MEMSZ    iRow;
 
   double *  pSpace;
   double ** ppArray;

   if (ppOldArray == NULL) {
      pSpace  = (double *)malloc(sizeof(double ) * nRow * nCol);
      ppArray = (double**)malloc(sizeof(double*) * nRow);
   } else {
      ppArray = (double**)realloc(ppOldArray, sizeof(double*) * nRow);
      pSpace  = (double *)realloc(ppOldArray[0],sizeof(double ) * nRow * nCol);
   }

   for (iRow = 0; iRow < nRow; iRow++) {
      /* Quantity (iRow*nCol) scales by sizeof(double) */
      ppArray[iRow] = pSpace + (iRow * nCol);
   }

   return ppArray;
}

/******************************************************************************/
/* Build an nRow x nCol matrix, in pointer-style.
 * Allocate one contiguous array of ints with  nRow*nCol elements.
 * Then create a set of nRow pointers, each of which points to the next nCol
 *  elements.
 */
int ** cciarray_rebuild_
  (MEMSZ    nRow,
   MEMSZ    nCol,
   int   ** ppOldArray)
{
   MEMSZ    iRow;
 
   int   *  pSpace;
   int   ** ppArray;

   if (ppOldArray == NULL) {
      pSpace  = (int *)malloc(sizeof(int ) * nRow * nCol);
      ppArray = (int**)malloc(sizeof(int*) * nRow);
   } else {
      ppArray = (int**)realloc(ppOldArray, sizeof(int*) * nRow);
      pSpace  = (int *)realloc(ppOldArray[0],sizeof(int ) * nRow * nCol);
   }

   for (iRow = 0; iRow < nRow; iRow++) {
      /* Quantity (iRow*nCol) scales by sizeof(int) */
      ppArray[iRow] = pSpace + (iRow * nCol);
   }

   return ppArray;
}

/******************************************************************************/
/* Free all memory allocated for an nRow x nCol matrix, as set up
 * with the routine ccarray_build_().
 */
void ccarray_free_
  (float ** ppArray,
   MEMSZ    nRow)
{
   /* Memory has been allocated in one contiguous chunk, so only free
    * ppArray[0] rather than every ppArray[i] for all i.
    */
   free((void *)ppArray[0]);
   free((void *)ppArray);
}

/******************************************************************************/
/* Free all memory allocated for an nRow x nCol matrix, as set up
 * with the routine ccdarray_build_().
 */
void ccdarray_free_
  (double ** ppArray,
   MEMSZ    nRow)
{
   /* Memory has been allocated in one contiguous chunk, so only free
    * ppArray[0] rather than every ppArray[i] for all i.
    */
   free((void *)ppArray[0]);
   free((void *)ppArray);
}

/******************************************************************************/
/* Free all memory allocated for an nRow x nCol matrix, as set up
 * with the routine cciarray_build_().
 */
void cciarray_free_
  (int   ** ppArray,
   MEMSZ    nRow)
{
   /* Memory has been allocated in one contiguous chunk, so only free
    * ppArray[0] rather than every ppArray[i] for all i.
    */
   free((void *)ppArray[0]);
   free((void *)ppArray);
}

/******************************************************************************/
/* Set all elements of an array equal to zero.
 * The array is assumed to be pointer-style, as allocated by ccarray_build_.
 */
void ccarray_zero_
  (float ** ppArray,
   MEMSZ    nRow,
   MEMSZ    nCol)
{
   MEMSZ    iRow;
   MEMSZ    iCol;

   for (iRow=0; iRow < nRow; iRow++) {
      for (iCol=0; iCol < nCol; iCol++) {
         ppArray[iRow][iCol] = 0.0;
      }
   }
}

/******************************************************************************/
/* Set all elements of a vector equal to zero.
 */
void ccvector_zero_
  (float *  pVector,
   MEMSZ    n)
{
   MEMSZ    i;
   for (i=0; i < n; i++) pVector[i] = 0.0;
}

/******************************************************************************/
/* Set all elements of a vector equal to zero.
 */
void ccdvector_zero_
  (double *  pVector,
   MEMSZ    n)
{
   MEMSZ    i;
   for (i=0; i < n; i++) pVector[i] = 0.0;
}

/******************************************************************************/
/* Set all elements of a vector equal to zero.
 */
void ccivector_zero_
  (int    *  pVector,
   MEMSZ    n)
{
   MEMSZ    i;
   for (i=0; i < n; i++) pVector[i] = 0.0;
}

