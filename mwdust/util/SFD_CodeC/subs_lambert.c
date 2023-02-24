
#include <string.h>
#include <stdio.h>
#include <stdlib.h> /* For call to malloc() */
#include "interface.h"
#include "subs_memory.h"
#include "subs_common_string.h"
#include "subs_common_math.h"
#include "subs_fits.h"
#include "subs_lambert.h"
#include <math.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#elif defined __GNUC__
#define EXPORT __attribute__((visibility("default")))
#else
#define EXPORT
#endif

#ifdef _WIN32
#include <Python.h>
PyMODINIT_FUNC PyInit_sfd_c(void)
{ // Python 3
   return NULL;
};
#endif

volatile sig_atomic_t interrupted = 0;
// handle CTRL-C
#ifndef _WIN32
void handle_sigint(int signum)
{
   interrupted = 1;
}
#else
#include <windows.h>
BOOL WINAPI CtrlHandler(DWORD fdwCtrlType)
{
   switch (fdwCtrlType)
   {
   // Handle the CTRL-C signal.
   case CTRL_C_EVENT:
      interrupted = 1;
      // needed to avoid other control handlers like python from being called before us
      return TRUE;
   default:
      return FALSE;
   }
}
#endif

char Label_lam_nsgp[]  = "LAM_NSGP";
char Label_lam_scal[]  = "LAM_SCAL";

uchar *  label_lam_nsgp  = (uchar*)Label_lam_nsgp;
uchar *  label_lam_scal  = (uchar*)Label_lam_scal;

// msvc unhappy about this section
#ifndef _WIN32
/******************************************************************************/
/* Fortran wrapper for reading Lambert FITS files */
void DECLARE(fort_lambert_getval)
  (char  *  pFileN,
   char  *  pFileS,
   void  *  pNGal,
   float *  pGall,
   float *  pGalb,
   void  *  pQInterp,
   void  *  pQNoloop,
   void  *  pQVerbose,
   float *  pOutput)
{
   int      iChar;
   int      qInterp;
   int      qNoloop;
   int      qVerbose;
   long     iGal;
   long     nGal;
   float *  pTemp;

   /* Truncate the Fortran-passed strings with a null,
    * in case they are padded with spaces */
   for (iChar=0; iChar < 80; iChar++)
    if (pFileN[iChar] == ' ') pFileN[iChar] = '\0';
   for (iChar=0; iChar < 80; iChar++)
    if (pFileS[iChar] == ' ') pFileS[iChar] = '\0';

   /* Select the 4-byte words passed by a Fortran call */
   if (sizeof(short) == 4) {
      nGal = *((short *)pNGal);
      qInterp = *((short *)pQInterp);
      qNoloop = *((short *)pQNoloop);
      qVerbose = *((short *)pQVerbose);
   } else if (sizeof(int) == 4) {
      nGal = *((int *)pNGal);
      qInterp = *((int *)pQInterp);
      qNoloop = *((int *)pQNoloop);
      qVerbose = *((int *)pQVerbose);
   } else if (sizeof(long) == 4) {
      nGal = *((long *)pNGal);
      qInterp = *((long *)pQInterp);
      qNoloop = *((long *)pQNoloop);
      qVerbose = *((long *)pQVerbose);
   }

   pTemp = lambert_getval(pFileN, pFileS, nGal, pGall, pGalb,
    qInterp, qNoloop, qVerbose);

   /* Copy results into Fortran-passed location for "pOutput",
    * assuming that memory has already been allocated */
   for (iGal=0; iGal < nGal; iGal++) pOutput[iGal] = pTemp[iGal];
}
#endif

/******************************************************************************/
/* Read one value at a time from NGP+SGP polar projections.
 * Set qInterp=1 to interpolate, or =0 otherwise.
 * Set qVerbose=1 to for verbose output, or =0 otherwise.
 */
EXPORT float * lambert_getval
  (char  *  pFileN,
   char  *  pFileS,
   long     nGal,
   float *  pGall,
   float *  pGalb,
   int      qInterp,
   int      qNoloop,
   int      qVerbose,
   int *err,
   tqdm_callback_type cb)
{
   int      iloop;
   int      iGal;
   int      ii;
   int      jj;
   int   *  pNS; /* 0 for NGP, 1 for SGP */
   int      nIndx;
   int   *  pIndx;
   int   *  pXPix;
   int   *  pYPix;
   int      xPix;
   int      yPix;
   int      xsize;
   DSIZE    pStart[2];
   DSIZE    pEnd[2];
   DSIZE    nSubimg;
   float *  pSubimg;
   float    dx;
   float    dy;
   float    xr;
   float    yr;
   float    pWeight[4];
   float    mapval;
   float *  pOutput;
   float *  pDX = NULL;
   float *  pDY = NULL;

   /* Variables for FITS files */
   int      qRead;
   int      numAxes;
   DSIZE *  pNaxis;
   char  *  pFileIn = NULL;
   HSIZE    nHead;
   uchar *  pHead;

   // Handle KeyboardInterrupt gracefully
   #ifndef _WIN32
      struct sigaction action;
      memset(&action, 0, sizeof(struct sigaction));
      action.sa_handler = handle_sigint;
      sigaction(SIGINT, &action, NULL);
   #else
      if (SetConsoleCtrlHandler(CtrlHandler, TRUE))
      {}
   #endif

   /* Allocate output data array */
   pNS = ccivector_build_(nGal);
   pOutput = ccvector_build_(nGal);

   /* Decide if each point should be read from the NGP or SGP projection */
   for (iGal=0; iGal < nGal; iGal++)
    pNS[iGal] = (pGalb[iGal] >= 0.0) ? 0 : 1; /* ==0 for NGP, ==1 for SGP */

   if (qNoloop == 0) {  /* LOOP THROUGH ONE POINT AT A TIME */

      /* Loop through first NGP then SGP */
      for (iloop=0; iloop < 2; iloop++) {
         qRead = 0;

         /* Loop through each data point */
         for (iGal=0; iGal < nGal; iGal++) {
                        if (interrupted)
            {
               *err = -10;
               break;
            }
            if (pNS[iGal] == iloop) {
               if ( cb ) cb(1);  // tqdm update for 1 star
               /* Read FITS header for this projection if not yet read */
               if (qRead == 0) {
                  if (iloop == 0) pFileIn = pFileN; else pFileIn = pFileS;
                  fits_read_file_fits_header_only_(pFileIn, &nHead, &pHead);
                  qRead = 1;
               }

               if (qInterp == 0) {  /* NEAREST PIXELS */

                  /* Determine the nearest pixel coordinates */
                  lambert_lb2pix(pGall[iGal], pGalb[iGal], nHead, pHead,
                   &xPix, &yPix);

                  pStart[0] = xPix;
                  pStart[1] = yPix;

                  /* Read one pixel value from data file */
                  fits_read_point_(pFileIn, nHead, pHead, pStart, &mapval);
                  pOutput[iGal] = mapval;

                  if (qVerbose != 0)
                   printf("%8.3f %7.3f %1d %8d %8d %12.5e\n",
                   pGall[iGal], pGalb[iGal], iloop, xPix, yPix, mapval);

               } else {  /* INTERPOLATE */

                  fits_compute_axes_(&nHead, &pHead, &numAxes, &pNaxis);

                  /* Determine the fractional pixel coordinates */
                  lambert_lb2fpix(pGall[iGal], pGalb[iGal], nHead, pHead,
                   &xr, &yr);
/* The following 4 lines introduced an erroneous 1/2-pixel shift
   (DJS 18-Mar-1999).
                  xPix = (int)(xr-0.5);
                  yPix = (int)(yr-0.5);
                  dx = xPix - xr + 1.5;
                  dy = yPix - yr + 1.5;
 */
                  xPix = (int)(xr);
                  yPix = (int)(yr);
                  dx = xPix - xr + 1.0;
                  dy = yPix - yr + 1.0;

                  /* Force pixel values to fall within the image boundaries */
                  if (xPix < 0) { xPix = 0; dx = 1.0; }
                  if (yPix < 0) { yPix = 0; dy = 1.0; }
                  if (xPix >= pNaxis[0]-1) { xPix = pNaxis[0]-2; dx = 0.0; }
                  if (yPix >= pNaxis[1]-1) { yPix = pNaxis[1]-2; dy = 0.0; }

                  pStart[0] = xPix;
                  pStart[1] = yPix;
                  pEnd[0] = xPix + 1;
                  pEnd[1] = yPix + 1;

                  /* Create array of weights */
                  pWeight[0] =    dx  *    dy  ;
                  pWeight[1] = (1-dx) *    dy  ;
                  pWeight[2] =    dx  * (1-dy) ;
                  pWeight[3] = (1-dx) * (1-dy) ;

                  /* Read 2x2 array from data file */
                  fits_read_subimg_(pFileIn, nHead, pHead, pStart, pEnd,
                   &nSubimg, &pSubimg);

                  pOutput[iGal] = 0.0;
                  for (jj=0; jj < 4; jj++)
                   pOutput[iGal] += pWeight[jj] * pSubimg[jj];

                  fits_free_axes_(&numAxes, &pNaxis);
                  ccfree_((void **)&pSubimg);

                  if (qVerbose != 0)
                   printf("%8.3f %7.3f %1d %9.3f %9.3f %12.5e\n",
                   pGall[iGal], pGalb[iGal], iloop, xr, yr, pOutput[iGal]);

               }  /* -- END NEAREST PIXEL OR INTERPOLATE -- */
            }
         // Back to default handler
         #ifndef _WIN32
                     action.sa_handler = SIG_DFL;
                     sigaction(SIGINT, &action, NULL);
         #endif
         }
      }

   } else {  /* READ FULL IMAGE */

      pIndx = ccivector_build_(nGal);
      pXPix = ccivector_build_(nGal);
      pYPix = ccivector_build_(nGal);
      if (qInterp != 0) {
         pDX = ccvector_build_(nGal);
         pDY = ccvector_build_(nGal);
      }

      /* Loop through first NGP then SGP */
      for (iloop=0; iloop < 2; iloop++) {

         /* Determine the indices of data points in this hemisphere */
         nIndx = 0;
         for (iGal=0; iGal < nGal; iGal++) {
            if (pNS[iGal] == iloop) {
               pIndx[nIndx] = iGal;
               nIndx++;
            }
         }

         /* Do not continue if no data points in this hemisphere */
         if (nIndx > 0) {

            /* Read FITS header for this projection */
            if (iloop == 0) pFileIn = pFileN; else pFileIn = pFileS;
            fits_read_file_fits_header_only_(pFileIn, &nHead, &pHead);

            if (qInterp == 0) {  /* NEAREST PIXELS */

               /* Determine the nearest pixel coordinates */
               for (ii=0; ii < nIndx; ii++) {
                  lambert_lb2pix(pGall[pIndx[ii]], pGalb[pIndx[ii]],
                   nHead, pHead, &pXPix[ii], &pYPix[ii]);
               }

               pStart[0] = ivector_minimum(nIndx, pXPix);
               pEnd[0] = ivector_maximum(nIndx, pXPix);
               pStart[1] = ivector_minimum(nIndx, pYPix);
               pEnd[1] = ivector_maximum(nIndx, pYPix);

               /* Read smallest subimage containing all points in this hemi */
               fits_read_subimg_(pFileIn, nHead, pHead, pStart, pEnd,
                &nSubimg, &pSubimg);
               xsize = pEnd[0] - pStart[0] + 1;

               /* Determine data values */
               for (ii=0; ii < nIndx; ii++) {
                  pOutput[pIndx[ii]] = pSubimg[ pXPix[ii]-pStart[0] +
                   (pYPix[ii]-pStart[1]) * xsize ];

               }

               ccfree_((void **)&pSubimg);

            } else {  /* INTERPOLATE */

               fits_compute_axes_(&nHead, &pHead, &numAxes, &pNaxis);

               /* Determine the fractional pixel coordinates */
               for (ii=0; ii < nIndx; ii++) {
                  lambert_lb2fpix(pGall[pIndx[ii]], pGalb[pIndx[ii]],
                   nHead, pHead, &xr, &yr);
/* The following 4 lines introduced an erroneous 1/2-pixel shift
   (DJS 03-Mar-2004).
                  pXPix[ii] = (int)(xr-0.5);
                  pYPix[ii] = (int)(yr-0.5);
                  pDX[ii] = pXPix[ii] - xr + 1.5;
                  pDY[ii] = pYPix[ii] - yr + 1.5;
*/
                  pXPix[ii] = (int)(xr);
                  pYPix[ii] = (int)(yr);
                  pDX[ii] = pXPix[ii] - xr + 1.0;
                  pDY[ii] = pYPix[ii] - yr + 1.0;

                  /* Force pixel values to fall within the image boundaries */
                  if (pXPix[ii] < 0) { pXPix[ii] = 0; pDX[ii] = 1.0; }
                  if (pYPix[ii] < 0) { pYPix[ii] = 0; pDY[ii] = 1.0; }
                  if (pXPix[ii] >= pNaxis[0]-1)
                   { pXPix[ii] = pNaxis[0]-2; pDX[ii] = 0.0; }
                  if (pYPix[ii] >= pNaxis[1]-1)
                   { pYPix[ii] = pNaxis[1]-2; pDY[ii] = 0.0; }

               }

               pStart[0] = ivector_minimum(nIndx, pXPix);
               pEnd[0] = ivector_maximum(nIndx, pXPix) + 1;
               pStart[1] = ivector_minimum(nIndx, pYPix);
               pEnd[1] = ivector_maximum(nIndx, pYPix) + 1;

               /* Read smallest subimage containing all points in this hemi */
               fits_read_subimg_(pFileIn, nHead, pHead, pStart, pEnd,
                &nSubimg, &pSubimg);
               xsize = pEnd[0] - pStart[0] + 1;

               /* Determine data values */
               for (ii=0; ii < nIndx; ii++) {
                  /* Create array of weights */
                  pWeight[0] =    pDX[ii]  *    pDY[ii]  ;
                  pWeight[1] = (1-pDX[ii]) *    pDY[ii]  ;
                  pWeight[2] =    pDX[ii]  * (1-pDY[ii]) ;
                  pWeight[3] = (1-pDX[ii]) * (1-pDY[ii]) ;

                  pOutput[pIndx[ii]] =
                    pWeight[0] * pSubimg[
                     pXPix[ii]-pStart[0]   + (pYPix[ii]-pStart[1]  )*xsize ]
                   +pWeight[1] * pSubimg[
                     pXPix[ii]-pStart[0]+1 + (pYPix[ii]-pStart[1]  )*xsize ]
                   +pWeight[2] * pSubimg[
                     pXPix[ii]-pStart[0]   + (pYPix[ii]-pStart[1]+1)*xsize ]
                   +pWeight[3] * pSubimg[
                     pXPix[ii]-pStart[0]+1 + (pYPix[ii]-pStart[1]+1)*xsize ] ;

               }

               fits_free_axes_(&numAxes, &pNaxis);
               ccfree_((void **)&pSubimg);

            }  /* -- END NEAREST PIXEL OR INTERPOLATE -- */
         }

      }

      ccivector_free_(pIndx);
      ccivector_free_(pXPix);
      ccivector_free_(pYPix);
      if (qInterp != 0) {
         ccvector_free_(pDX);
         ccvector_free_(pDY);
      }
   }

   /* Free the memory allocated for the FITS header 
      (Moved outside previous brace by Chris Stoughton 19-Jan-1999) */
   fits_dispose_array_(&pHead);

   /* Deallocate output data array */
   ccivector_free_(pNS);

   return pOutput;
}

/******************************************************************************/
/* Transform from galactic (l,b) coordinates to fractional (x,y) pixel location.
 * Latitude runs clockwise from X-axis for NGP, counterclockwise for SGP.
 * This function returns the ZERO-INDEXED pixel position.
 * Updated 04-Mar-1999 to allow ZEA coordinate convention for the same
 * projection.
 */
void lambert_lb2fpix
  (float    gall,   /* Galactic longitude */
   float    galb,   /* Galactic latitude */
   HSIZE    nHead,
   uchar *  pHead,
   float *  pX,     /* X position in pixels from the center */
   float *  pY)     /* Y position in pixels from the center */
{
   int      q1;
   int      q2;
   int      nsgp;
   float    scale;
   float    crval1;
   float    crval2;
   float    crpix1;
   float    crpix2;
   float    cdelt1;
   float    cdelt2;
   float    cd1_1;
   float    cd1_2;
   float    cd2_1;
   float    cd2_2;
   float    lonpole;
   float    xr;
   float    yr;
   float    theta;
   float    phi;
   float    Rtheta;
   float    denom;
   static double dradeg = 180 / 3.1415926534;
   char  *  pCtype1;
   char  *  pCtype2;

   fits_get_card_string_(&pCtype1, label_ctype1, &nHead, &pHead);
   fits_get_card_string_(&pCtype2, label_ctype2, &nHead, &pHead);
   fits_get_card_rval_(&crval1, label_crval1, &nHead, &pHead);
   fits_get_card_rval_(&crval2, label_crval2, &nHead, &pHead);
   fits_get_card_rval_(&crpix1, label_crpix1, &nHead, &pHead);
   fits_get_card_rval_(&crpix2, label_crpix2, &nHead, &pHead);

   if (strcmp(pCtype1, "LAMBERT--X")  == 0 &&
       strcmp(pCtype2, "LAMBERT--Y")  == 0) {

      fits_get_card_ival_(&nsgp, label_lam_nsgp, &nHead, &pHead);
      fits_get_card_rval_(&scale, label_lam_scal, &nHead, &pHead);

      lambert_lb2xy(gall, galb, nsgp, scale, &xr, &yr);
      *pX = xr + crpix1 - crval1 - 1.0;
      *pY = yr + crpix2 - crval2 - 1.0;

   } else if (strcmp(pCtype1, "GLON-ZEA")  == 0 &&
              strcmp(pCtype2, "GLAT-ZEA")  == 0) { 

      q1 = fits_get_card_rval_(&cdelt1, label_cdelt1, &nHead, &pHead);
      q2 = fits_get_card_rval_(&cdelt2, label_cdelt2, &nHead, &pHead);
      if (q1 == TRUE && q2 == TRUE) {
          cd1_1 = cdelt1;
          cd1_2 = 0.0;
          cd2_1 = 0.0;
          cd2_2 = cdelt2;
       } else {
         fits_get_card_rval_(&cd1_1, label_cd1_1, &nHead, &pHead);
         fits_get_card_rval_(&cd1_2, label_cd1_2, &nHead, &pHead);
         fits_get_card_rval_(&cd2_1, label_cd2_1, &nHead, &pHead);
         fits_get_card_rval_(&cd2_2, label_cd2_2, &nHead, &pHead);
      }
      q1 = fits_get_card_rval_(&lonpole, label_lonpole, &nHead, &pHead);
      if (q1 == FALSE) lonpole = 180.0; /* default value */

      /* ROTATION */
      /* Equn (4) - degenerate case */
      if (crval2 > 89.9999) {
         theta = galb;
         phi = gall + 180.0 + lonpole - crval1;
      } else if (crval2 < -89.9999) {
         theta = -galb;
         phi = lonpole + crval1 - gall;
      } else {
         printf("ERROR: Unsupported projection!!!\n");
         /* Assume it's an NGP projection ... */
         theta = galb;
         phi = gall + 180.0 + lonpole - crval1;
      }

      /* Put phi in the range [0,360) degrees */
      phi = phi - 360.0 * floor(phi/360.0);

      /* FORWARD MAP PROJECTION */
      /* Equn (26) */
      Rtheta = 2.0 * dradeg * sin((0.5 / dradeg) * (90.0 - theta));

      /* Equns (10), (11) */
      xr = Rtheta * sin(phi / dradeg);
      yr = - Rtheta * cos(phi / dradeg);

      /* SCALE FROM PHYSICAL UNITS */
      /* Equn (3) after inverting the matrix */
      denom = cd1_1 * cd2_2 - cd1_2 * cd2_1;
      *pX = (cd2_2 * xr - cd1_2 * yr) / denom + (crpix1 - 1.0);
      *pY = (cd1_1 * yr - cd2_1 * xr) / denom + (crpix2 - 1.0);

   } else {

      *pX = -99.0;
      *pY = -99.0;

   }

   ccfree_((void **)&pCtype1);
   ccfree_((void **)&pCtype2);
}

/******************************************************************************/
/* Transform from galactic (l,b) coordinates to (ix,iy) pixel location.
 * Latitude runs clockwise from X-axis for NGP, counterclockwise for SGP.
 * This function returns the ZERO-INDEXED pixel position.
 * 
 */
void lambert_lb2pix
  (float    gall,   /* Galactic longitude */
   float    galb,   /* Galactic latitude */
   HSIZE    nHead,
   uchar *  pHead,
   int   *  pIX,    /* X position in pixels from the center */
   int   *  pIY)    /* Y position in pixels from the center */
{
   int      naxis1;
   int      naxis2;
   float    xr;
   float    yr;

   fits_get_card_ival_(&naxis1, label_naxis1, &nHead, &pHead);
   fits_get_card_ival_(&naxis2, label_naxis2, &nHead, &pHead);

   lambert_lb2fpix(gall, galb, nHead, pHead, &xr, &yr);
   *pIX = floor(xr + 0.5);
   *pIY = floor(yr + 0.5);

   /* Force bounds to be valid at edge, for ex at l=0,b=0 */
   //printf("NAXES %d %d\n", naxis1,naxis2);
   if (*pIX >= naxis1) *pIX = naxis1 - 1;
   if (*pIY >= naxis2) *pIY = naxis2 - 1;
}

/******************************************************************************/
/* Transform from galactic (l,b) coordinates to (x,y) coordinates from origin.
 * Latitude runs clockwise from X-axis for NGP, counterclockwise for SGP.
 */
void lambert_lb2xy
  (float    gall,   /* Galactic longitude */
   float    galb,   /* Galactic latitude */
   int      nsgp,   /* +1 for NGP projection, -1 for SGP */
   float    scale,  /* Radius of b=0 to b=90 degrees in pixels */
   float *  pX,     /* X position in pixels from the center */
   float *  pY)     /* Y position in pixels from the center */
{
   double   rho;
   static double dradeg = 180 / 3.1415926534;

   rho = sqrt(1. - nsgp * sin(galb/dradeg));
/* The following two lines were modified by Hans Schwengeler (17-Mar-1999)
   to get this to work on a Tur64 Unix 4.0E (DEC Alpha).  It appears that
   float and double on not the same on this machine.
   *pX = rho * cos(gall/dradeg) * scale;
   *pY = -nsgp * rho * sin(gall/dradeg) * scale;
*/
   *pX = rho * cos((float)((double)gall/dradeg)) * scale;
   *pY = -nsgp * rho * sin((float)((double)gall/dradeg)) * scale;
}
/******************************************************************************/
/* Find the min value of the nData elements of an integer array pData[].
 */
int ivector_minimum
  (int      nData,
   int   *  pData)
{
   int      i;
   int      vmin;

   vmin = pData[0];
   for (i=1; i<nData; i++) if (pData[i] < vmin) vmin=pData[i];

   return vmin;
}

/******************************************************************************/
/* Find the max value of the nData elements of an integer array pData[].
 */
int ivector_maximum
  (int      nData,
   int   *  pData)
{
   int      i;
   int      vmax;

   vmax = pData[0];
   for (i=1; i<nData; i++) if (pData[i] > vmax) vmax=pData[i];

   return vmax;
}

/******************************************************************************/