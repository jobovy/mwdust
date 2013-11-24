
#ifndef __INCsubs_memory_h
#define __INCsubs_memory_h

typedef size_t MEMSZ;

#ifdef OLD_SUNCC
void memmove
  (void  *  s,
   const void  *  ct,
   MEMSZ    n);
#endif
void ccalloc_resize_
  (MEMSZ *  pOldMemSize,
   MEMSZ *  pNewMemSize,
   void  ** ppData);
void ccrealloc_
  (MEMSZ *  pMemSize,
   void  ** ppData);
void ccalloc_init
  (MEMSZ *  pMemSize,
   void  ** ppData);
void ccalloc_
  (MEMSZ *  pMemSize,
   void  ** ppData);
void ccfree_
  (void  ** ppData);
float * ccvector_build_
  (MEMSZ    n);
double * ccdvector_build_
  (MEMSZ    n);
int * ccivector_build_
  (MEMSZ    n);
float ** ccpvector_build_
  (MEMSZ    n);
float *** ccppvector_build_
  (MEMSZ    n);
float * ccvector_rebuild_
  (MEMSZ    n,
   float *  pOldVector);
double * ccdvector_rebuild_
  (MEMSZ    n,
   double *  pOldVector);
int * ccivector_rebuild_
  (MEMSZ    n,
   int   *  pOldVector);
float ** ccpvector_rebuild_
  (MEMSZ    n,
   float ** ppOldVector);
float *** ccppvector_rebuild_
  (MEMSZ    n,
   float *** pppOldVector);
void ccvector_free_
  (float *  pVector);
void ccdvector_free_
  (double *  pVector);
void ccivector_free_
  (int   *  pVector);
void ccpvector_free_
  (float ** ppVector);
void ccppvector_free_
  (float *** pppVector);
float ** ccarray_build_
  (MEMSZ    nRow,
   MEMSZ    nCol);
double ** ccdarray_build_
  (MEMSZ    nRow,
   MEMSZ    nCol);
int ** cciarray_build_
  (MEMSZ    nRow,
   MEMSZ    nCol);
float ** ccarray_rebuild_
  (MEMSZ    nRow,
   MEMSZ    nCol,
   float ** ppOldArray);
double ** ccdarray_rebuild_
  (MEMSZ    nRow,
   MEMSZ    nCol,
   double ** ppOldArray);
int ** cciarray_rebuild_
  (MEMSZ    nRow,
   MEMSZ    nCol,
   int   ** ppOldArray);
void ccarray_free_
  (float ** ppArray,
   MEMSZ    nRow);
void ccdarray_free_
  (double ** ppArray,
   MEMSZ    nRow);
void cciarray_free_
  (int   ** ppArray,
   MEMSZ    nRow);
void ccarray_zero_
  (float ** ppArray,
   MEMSZ    nRow,
   MEMSZ    nCol);
void ccvector_zero_
  (float *  pVector,
   MEMSZ    n);
void ccdvector_zero_
  (double *  pVector,
   MEMSZ    n);
void ccivector_zero_
  (int    *  pVector,
   MEMSZ    n);

#endif /* __INCsubs_memory_h */
