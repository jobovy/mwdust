
#ifndef __INCsubs_lambert_h
#define __INCsubs_lambert_h

void DECLARE(fort_lambert_getval)
  (char  *  pFileN,
   char  *  pFileS,
   void  *  pNGal,
   float *  pGall,
   float *  pGalb,
   void  *  pQInterp,
   void  *  pQNoloop,
   void  *  pQVerbose,
   float *  pOutput);
float * lambert_getval
  (char  *  pFileN,
   char  *  pFileS,
   long     nGal,
   float *  pGall,
   float *  pGalb,
   int      qInterp,
   int      qNoloop,
   int      qVerbose);
void lambert_lb2fpix
  (float    gall,   /* Galactic longitude */
   float    galb,   /* Galactic latitude */
   HSIZE    nHead,
   uchar *  pHead,
   float *  pX,     /* X position in pixels from the center */
   float *  pY);    /* Y position in pixels from the center */
void lambert_lb2pix
  (float    gall,   /* Galactic longitude */
   float    galb,   /* Galactic latitude */
   HSIZE    nHead,
   uchar *  pHead,
   int   *  pIX,    /* X position in pixels from the center */
   int   *  pIY);   /* Y position in pixels from the center */
void lambert_lb2xy
  (float    gall,   /* Galactic longitude */
   float    galb,   /* Galactic latitude */
   int      nsgp,   /* +1 for NGP projection, -1 for SGP */
   float    scale,  /* Radius of b=0 to b=90 degrees in pixels */
   float *  pX,     /* X position in pixels from the center */
   float *  pY);    /* Y position in pixels from the center */
int ivector_minimum
  (int      nData,
   int   *  pData);
int ivector_maximum
  (int      nData,
   int   *  pData);


extern uchar * label_lam_nsgp;
extern uchar * label_lam_scal;

#endif /* __INCsubs_lambert_h */
