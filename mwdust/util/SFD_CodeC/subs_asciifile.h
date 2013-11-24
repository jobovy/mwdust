
#ifndef __INCsubs_asciifile_h
#define __INCsubs_asciifile_h
 
int asciifile_read_colmajor
  (char     pFileName[],
   int      numColsMax,
   int   *  pNRows,
   int   *  pNCols,
   float ** ppData);
int asciifile_read_rowmajor
  (char     pFileName[],
   int      numColsMax,
   int   *  pNRows,
   int   *  pNCols,
   float ** ppData);
char * asciifile_read_line
  (int      filenum,
   int      numColsMax,
   int   *  pNValues,
   float *  values);

#endif /* __INCsubs_asciifile_h */
