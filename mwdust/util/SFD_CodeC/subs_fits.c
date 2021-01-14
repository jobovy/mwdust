/******************************************************************************/
/*
 * Subroutines to read and write FITS format files.
 * Note all variables are passed as pointers, so the routines can be called
 * by either C or Fortran programs.
 * Remember to omit the final underscore for calls from Fortran,
 * so one says 'call fits_add_card(...)' or 'i=fits_add_card(...)' in Fortran,
 * but 'i=fits_add_card_(...)' in C.
 *
 * D Schlegel -- Berkeley -- ANSI C
 * Mar 1992  DJS  Created
 * Dec 1993  DJS  Major revisions to allow dynamic memory allocations.
 */
/******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h> /* For function toupper() */
#include "subs_fits.h"
#include "subs_inoutput.h"
#include "subs_memory.h"

#define min(a,b) ( ((a) < (b)) ? (a) : (b) )
#define max(a,b) ( ((a) > (b)) ? (a) : (b) )
#define TRUE  1
#define FALSE 0

char Datum_zero[]    = "\0\0\0\0";
char Label_airmass[] = "AIRMASS ";
char Label_bitpix[]  = "BITPIX  ";
char Label_blank[]   = "BLANK   ";
char Label_bscale[]  = "BSCALE  ";
char Label_bzero[]   = "BZERO   ";
char Label_ctype1[]  = "CTYPE1  ";
char Label_ctype2[]  = "CTYPE2  ";
char Label_cdelt1[]  = "CDELT1  ";
char Label_cdelt2[]  = "CDELT2  ";
char Label_cd1_1[]   = "CD1_1   ";
char Label_cd1_2[]   = "CD1_2   ";
char Label_cd2_1[]   = "CD2_1   ";
char Label_cd2_2[]   = "CD2_2   ";
char Label_latpole[] = "LATPOLE ";
char Label_lonpole[] = "LONPOLE ";
char Label_crpix1[]  = "CRPIX1  ";
char Label_crpix2[]  = "CRPIX2  ";
char Label_crval1[]  = "CRVAL1  ";
char Label_crval2[]  = "CRVAL2  ";
char Label_date_obs[]= "DATE-OBS";
char Label_dec[]     = "DEC     ";
char Label_empty[]   = "        ";
char Label_end[]     = "END     ";
char Label_exposure[]= "EXPOSURE";
char Label_extend[]  = "EXTEND  ";
char Label_filtband[]= "FILTBAND";
char Label_filter[]  = "FILTER  ";
char Label_ha[]      = "HA      ";
char Label_instrume[]= "INSTRUME";
char Label_lamord[]  = "LAMORD  ";
char Label_loss[]    = "LOSS    ";
char Label_naxis[]   = "NAXIS   ";
char Label_naxis1[]  = "NAXIS1  ";
char Label_naxis2[]  = "NAXIS2  ";
char Label_object[]  = "OBJECT  ";
char Label_observer[]= "OBSERVER";
char Label_pa[]      = "PA      ";
char Label_platescl[]= "PLATESCL";
char Label_ra[]      = "RA      ";
char Label_rnoise[]  = "RNOISE  ";
char Label_rota[]    = "ROTA    ";
char Label_seeing[]  = "SEEING  ";
char Label_skyrms[]  = "SKYRMS  ";
char Label_skyval[]  = "SKYVAL  ";
char Label_slitwidt[]= "SLITWIDT";
char Label_st[]      = "ST      ";
char Label_telescop[]= "TELESCOP";
char Label_time[]    = "TIME    ";
char Label_tub[]     = "TUB     ";
char Label_ut[]      = "UT      ";
char Label_vhelio[]  = "VHELIO  ";
char Label_vminusi[] = "VMINUSI ";
char Card_simple[] =
   "SIMPLE  =                    T          "\
   "                                        ";
char Card_empty[] =
   "                                        "\
   "                                        ";
char Card_null[] =
   "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"\
   "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"\
   "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"\
   "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0";
char Card_end[] =
   "END                                     "\
   "                                        ";
char Text_T[] = "T";
char Text_F[] = "F";

uchar *  datum_zero    = (uchar*)Datum_zero;
uchar *  label_airmass = (uchar*)Label_airmass;
uchar *  label_bitpix  = (uchar*)Label_bitpix;
uchar *  label_blank   = (uchar*)Label_blank;
uchar *  label_bscale  = (uchar*)Label_bscale;
uchar *  label_bzero   = (uchar*)Label_bzero;
uchar *  label_ctype1  = (uchar*)Label_ctype1;
uchar *  label_ctype2  = (uchar*)Label_ctype2;
uchar *  label_cdelt1  = (uchar*)Label_cdelt1;
uchar *  label_cdelt2  = (uchar*)Label_cdelt2;
uchar *  label_cd1_1   = (uchar*)Label_cd1_1;
uchar *  label_cd1_2   = (uchar*)Label_cd1_2;
uchar *  label_cd2_1   = (uchar*)Label_cd2_1;
uchar *  label_cd2_2   = (uchar*)Label_cd2_2;
uchar *  label_latpole = (uchar*)Label_latpole;
uchar *  label_lonpole = (uchar*)Label_lonpole;
uchar *  label_crpix1  = (uchar*)Label_crpix1;
uchar *  label_crpix2  = (uchar*)Label_crpix2;
uchar *  label_crval1  = (uchar*)Label_crval1;
uchar *  label_crval2  = (uchar*)Label_crval2;
uchar *  label_date_obs= (uchar*)Label_date_obs;
uchar *  label_dec     = (uchar*)Label_dec;
uchar *  label_empty   = (uchar*)Label_empty;
uchar *  label_end     = (uchar*)Label_end;
uchar *  label_exposure= (uchar*)Label_exposure;
uchar *  label_extend  = (uchar*)Label_extend;
uchar *  label_filtband= (uchar*)Label_filtband;
uchar *  label_filter  = (uchar*)Label_filter;
uchar *  label_ha      = (uchar*)Label_ha;
uchar *  label_instrume= (uchar*)Label_instrume;
uchar *  label_lamord  = (uchar*)Label_lamord;
uchar *  label_loss    = (uchar*)Label_loss;
uchar *  label_naxis   = (uchar*)Label_naxis;
uchar *  label_naxis1  = (uchar*)Label_naxis1;
uchar *  label_naxis2  = (uchar*)Label_naxis2;
uchar *  label_object  = (uchar*)Label_object;
uchar *  label_observer= (uchar*)Label_observer;
uchar *  label_pa      = (uchar*)Label_pa;
uchar *  label_platescl= (uchar*)Label_platescl;
uchar *  label_ra      = (uchar*)Label_ra;
uchar *  label_rnoise  = (uchar*)Label_rnoise;
uchar *  label_rota    = (uchar*)Label_rota;
uchar *  label_seeing  = (uchar*)Label_seeing;
uchar *  label_skyrms  = (uchar*)Label_skyrms;
uchar *  label_skyval  = (uchar*)Label_skyval;
uchar *  label_slitwidt= (uchar*)Label_slitwidt;
uchar *  label_st      = (uchar*)Label_st;
uchar *  label_telescop= (uchar*)Label_telescop;
uchar *  label_time    = (uchar*)Label_time;
uchar *  label_tub     = (uchar*)Label_tub;
uchar *  label_ut      = (uchar*)Label_ut;
uchar *  label_vhelio  = (uchar*)Label_vhelio;
uchar *  label_vminusi = (uchar*)Label_vminusi;
uchar *  card_simple   = (uchar*)Card_simple;
uchar *  card_empty    = (uchar*)Card_empty;
uchar *  card_null     = (uchar*)Card_null;
uchar *  card_end      = (uchar*)Card_end;
uchar *  text_T        = (uchar*)Text_T;
uchar *  text_F        = (uchar*)Text_F;

/******************************************************************************/
/*
 * Read in FITS format data.  Assume the header is a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * Any data that follows is ignored.
 */
void fits_read_file_fits_header_only_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      fileNum;
   char     pPrivR[] = "r\0";

   inoutput_open_file(&fileNum, pFileName, pPrivR);

   /* Read header */
   fits_read_fits_header_(&fileNum, pNHead, ppHead);

   inoutput_close_file(fileNum);
}

/******************************************************************************/
/*
 * Read in header cards that are in ASCII format, for example as output
 * by IRAF with carraige returns after lines that are not even 80 characters.
 * The data is read into an array in FITS format.
 *
 * Return IO_GOOD if the file exists, and IO_BAD otherwise.
 */
int fits_read_file_ascii_header_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      cLen;
   int      fileNum;
   int      maxLen = 80;
   int      qExist;
   char     pPrivR[] = "r\0";
   uchar    pCard[80];

   qExist = inoutput_open_file(&fileNum, pFileName, pPrivR);

   if (qExist == IO_GOOD) {
      /* Read the header into memory until the end of file */
      *pNHead = 0;
      while (fgets((char *)pCard, maxLen, pFILEfits[fileNum]) != NULL) {
         /* Replace the /0 and remainder of card with blanks */
         for (cLen=strlen((const char *)pCard); cLen < 80; cLen++)
          pCard[cLen]=' ';

         fits_add_card_(pCard, pNHead, ppHead);
      }

      /* If no END card, then add one */
      if (fits_find_card_(label_end, pNHead, ppHead) == *pNHead) {
         fits_add_card_(card_end, pNHead, ppHead);
      }

      /* Close the file */
      inoutput_close_file(fileNum);
   }

   return qExist;
}

/******************************************************************************/
/*
 * Read in FITS format data.  Assume the header is a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * The data follows as either real values or as integer values
 * that should be scaled by the BZERO and BSCALE values.  The data
 * format is determined by the BITPIX card in the header.
 * The data is rescaled to 32-bit reals.
 * Also, the BITPIX card in the header is changed to -32.
 * Memory is dynamically allocated for the header and data arrays.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than indicated in the header, in which case the difference is returned.
 */
DSIZE fits_read_file_fits_r4_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   float ** ppData)
{
   int      bitpix;
   DSIZE    retval;

   retval = fits_read_file_fits_noscale_(pFileName, pNHead,
    ppHead, pNData, &bitpix, (uchar **)ppData);

   /* Convert data to real*4 if not already */
   fits_data_to_r4_(pNHead, ppHead, pNData, (uchar **)ppData);

   return retval;
}

/******************************************************************************/
/*
 * Read in FITS format data.  Assume the header is a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * The data follows as either real values or as integer values
 * that should be scaled by the BZERO and BSCALE values.  The data
 * format is determined by the BITPIX card in the header.
 * The data is rescaled to 16-bit integers.
 * Also, the BITPIX card in the header is changed to 16.
 * Memory is dynamically allocated for the header and data arrays.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than indicated in the header, in which case the difference is returned.
 */
DSIZE fits_read_file_fits_i2_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   short int   ** ppData)
{
   int      bitpix;
   DSIZE    retval;

   retval = fits_read_file_fits_noscale_(pFileName, pNHead,
    ppHead, pNData, &bitpix, (uchar **)ppData);

   /* Convert data to integer*4 if not already */
   fits_data_to_i2_(pNHead, ppHead, pNData, (uchar **)ppData);

   return retval;
}

/******************************************************************************/
/*
 * Read subimage from a FITS format data file, indexed from pStart to pEnd
 * in each dimension.
 *
 * The header is assumed to already be read using
 * fits_read_file_fits_header_only_(), to avoid reading it upon every
 * call to this routine.  The axis dimensions and BITPIX are read from
 * the header that is passed.  The dimensions of pLoc must agree with
 * the dimensions specified by NAXIS in this header.
 *
 * The data values are rescaled to 32-bit reals.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than requested, in which case the difference is returned.
 */

DSIZE fits_read_subimg_
  (char     pFileName[],
   HSIZE    nHead,
   uchar *  pHead,
   DSIZE *  pStart,
   DSIZE *  pEnd,
   DSIZE *  pNVal,
   float ** ppVal)
{
   int      bitpix;
   DSIZE    iloc;
   DSIZE    nExpect;
   int      size;
   MEMSZ    memSize;
   int      iAxis;
   int      numAxes;
   DSIZE *  pNaxis;
   float    bscale;
   float    bzero;
   uchar *  pData;

   int      fileNum;
   char     pPrivR[] = "r\0";

   inoutput_open_file(&fileNum, pFileName, pPrivR);

   /* Skip header */
   fits_skip_header_(&fileNum);

   /* From the given header, read BITPIX and PNAXIS */
   fits_get_card_ival_(&bitpix, label_bitpix, &nHead, &pHead);
   fits_compute_axes_(&nHead, &pHead, &numAxes, &pNaxis);

   /* Allocate memory for output */
   nExpect = 1;
   for (iAxis=0; iAxis < numAxes; iAxis++)
    nExpect *= (pEnd[iAxis] - pStart[iAxis] + 1);
   size = fits_size_from_bitpix_(&bitpix);
   memSize = size * nExpect;
   ccalloc_(&memSize, (void **)&pData);

   *pNVal = 0;
   fits_read_subimg1(numAxes, pNaxis, pStart, pEnd, fileNum, bitpix,
    pNVal, pData);
#ifdef LITTLE_ENDIAN
   fits_byteswap(bitpix, *pNVal, pData);
#endif

   /* Convert data to real*4 if not already */
   if (bitpix == -32) {
      *ppVal = (float *)pData;
   } else {
      /* Get the scaling parameters from the header */
      if (fits_get_card_rval_(&bscale, (uchar *)Label_bscale, &nHead, &pHead)
       == FALSE) {
         bscale = 1.0;  /* Default value for BSCALE */
      }
      if (fits_get_card_rval_(&bzero , (uchar *)Label_bzero , &nHead, &pHead)
       == FALSE) {
         bzero = 0.0;  /* Default value for BZERO */
      }
 
      memSize = sizeof(float) * nExpect;
      ccalloc_(&memSize, (void **)ppVal);
      for (iloc=0; iloc < *pNVal; iloc++)
       (*ppVal)[iloc] = fits_get_rval_(&iloc, &bitpix, &bscale, &bzero, &pData);
   }
 
   inoutput_close_file(fileNum);

   /* Plug a memory leak - Chris Stoughton 19-Jan-1999 */
   fits_free_axes_(&numAxes, &pNaxis);

   return (nExpect - (*pNVal));
}

void fits_read_subimg1
  (int      nel,
   DSIZE *  pNaxis,
   DSIZE *  pStart,
   DSIZE *  pEnd,
   int      fileNum,
   int      bitpix,
   DSIZE *  pNVal,
   uchar *  pData)
{
   int      iloop;
   int      ii;
   int      ipos;
   int      size;
   DSIZE    nskip;
   DSIZE    nread;
   FILE  *  pFILEin;

   pFILEin = pFILEfits[fileNum];
   size = fits_size_from_bitpix_(&bitpix);

   /* Skip "nskip" points */
   nskip = pStart[nel-1];
   for (ii=0; ii < nel-1; ii++) nskip = nskip * pNaxis[ii];
   ipos = ftell(pFILEin);
   fseek(pFILEin, (ipos + size*nskip), 0);

   if (nel > 1) {
      for (iloop=0; iloop < pEnd[nel-1]-pStart[nel-1]+1; iloop++)
       fits_read_subimg1(nel-1, pNaxis, pStart, pEnd, fileNum, bitpix,
        pNVal, pData);
   } else {
      nread = pEnd[0]-pStart[0]+1;

      /* Read in "nread" points */
      *pNVal += (int)fread(&pData[(*pNVal)*size], size, nread, pFILEin);
   }

   /* Skip "nskip" points */
   nskip = pNaxis[nel-1] - pEnd[nel-1] - 1;
   for (ii=0; ii < nel-1; ii++) nskip = nskip * pNaxis[ii];
   ipos = ftell(pFILEin);
   fseek(pFILEin, (ipos + size*nskip), 0);
}

/******************************************************************************/
/*
 * Read in one element from a FITS format data file, indexed by the
 * values in pLoc.
 *
 * The header is assumed to already be read using
 * fits_read_file_fits_header_only_(), to avoid reading it upon every
 * call to this routine.  The axis dimensions and BITPIX are read from
 * the header that is passed.  The dimensions of pLoc must agree with
 * the dimensions specified by NAXIS in this header.
 *
 * The data value is rescaled to a 32-bit real.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than requested (1), in which case the difference (1) is returned.
 */

DSIZE fits_read_point_
  (char     pFileName[],
   HSIZE    nHead,
   uchar *  pHead,
   DSIZE *  pLoc,
   float *  pValue)
{
   int      bitpix;
   DSIZE    iloc;
   int      nmult;
   int      size;
   MEMSZ    memSize;
   int      iAxis;
   int      numAxes;
   DSIZE *  pNaxis;
   float    bscale;
   float    bzero;
   uchar *  pData;
   DSIZE    retval;

   int      fileNum;
   int      ipos;
   char     pPrivR[] = "r\0";
   FILE  *  pFILEin;

   inoutput_open_file(&fileNum, pFileName, pPrivR);

   /* Skip header */
   fits_skip_header_(&fileNum);

   /* From the given header, read BITPIX and PNAXIS */
   fits_get_card_ival_(&bitpix, label_bitpix, &nHead, &pHead);
   fits_compute_axes_(&nHead, &pHead, &numAxes, &pNaxis);

   /* Find the 1-dimensional index for the data point requested */
   iloc = 0;
   nmult = 1;
   for (iAxis=0; iAxis < numAxes; iAxis++) {
      iloc = iloc + pLoc[iAxis] * nmult;
      nmult = nmult * pNaxis[iAxis];
   }

   /* Read one element from the data file */
   pFILEin = pFILEfits[fileNum];
   ipos = ftell(pFILEin);
   size = fits_size_from_bitpix_(&bitpix);
   memSize = size;
   ccalloc_(&memSize, (void **)&pData);
   fseek(pFILEin, (ipos + size*iloc), 0);
   retval = 1 - (int)fread(pData, size, 1, pFILEin);
#ifdef LITTLE_ENDIAN
   fits_byteswap(bitpix, 1, pData);
#endif

   /* Convert data to real*4 if not already */
   if (bitpix == -32) {
      *pValue = *( (float *)pData );
   } else {
      /* Get the scaling parameters from the header */
      if (fits_get_card_rval_(&bscale, (uchar *)Label_bscale, &nHead, &pHead)
       == FALSE) {
         bscale = 1.0;  /* Default value for BSCALE */
      }
      if (fits_get_card_rval_(&bzero , (uchar *)Label_bzero , &nHead, &pHead)
       == FALSE) {
         bzero = 0.0;  /* Default value for BZERO */
      }

      iloc = 0;
      *pValue = fits_get_rval_(&iloc, &bitpix, &bscale, &bzero, &pData);
   }

   inoutput_close_file(fileNum);

   /* Plug a memory leak - D. Schlegel 06-Feb-1999 */
   fits_free_axes_(&numAxes, &pNaxis);

   return retval;
}

/******************************************************************************/
/*
 * Read in FITS format data.  Assume the header is a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * The data follows as either real values or as integer values
 * that should be scaled by the BZERO and BSCALE values.  The data
 * format is determined by the BITPIX card in the header.
 * Memory is dynamically allocated for the header and data arrays.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than indicated in the header, in which case the difference is returned.
 */
DSIZE fits_read_file_fits_noscale_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   int   *  pBitpix,
   uchar ** ppData)
{
   int      fileNum;
   DSIZE    retval;
   char     pPrivR[] = "r\0";

   inoutput_open_file(&fileNum, pFileName, pPrivR);

   /* Read header */
   fits_read_fits_header_(&fileNum, pNHead, ppHead);

   /* From the header, read BITPIX and determine the number of data points */
   *pNData = fits_compute_ndata_(pNHead, ppHead);
   fits_get_card_ival_(pBitpix, label_bitpix, pNHead, ppHead);

   /* Read data */
   retval = fits_read_fits_data_(&fileNum, pBitpix, pNData, ppData);

   inoutput_close_file(fileNum);
   return retval;
}

/******************************************************************************/
/*
 * Read in EXTENDED FITS format data.  Assume the header is a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * In addition, allow for an extended header file.  (But always reads
 * exactly one additional header.)
 * The data follows as either real values or as integer values
 * that should be scaled by the BZERO and BSCALE values.  The data
 * format is determined by the BITPIX card in the header.
 * Memory is dynamically allocated for the header and data arrays.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than indicated in the header, in which case the difference is returned.
 */
DSIZE fits_read_file_xfits_noscale_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   HSIZE *  pNXhead,
   uchar ** ppXHead,
   DSIZE *  pNData,
   int   *  pBitpix,
   uchar ** ppData)
{

   int      fileNum;
   HSIZE    iCard;
   HSIZE *  pTempN;
   DSIZE    retval;
   uchar    pExtend[40];
   uchar *  pTempHead;
   char     pPrivR[] = "r\0";

   inoutput_open_file(&fileNum, pFileName, pPrivR);

   /* Read header */
   fits_read_fits_header_(&fileNum, pNHead, ppHead);

   /* Read extended header(if it exists) */
   pTempN = pNHead;
   pTempHead = *ppHead;
   iCard = fits_find_card_(label_extend, pNHead, ppHead);
   if (iCard < *pNHead)
    sscanf(&(*ppHead)[iCard*80+10], "%s", pExtend);
   if (strcmp((const char *)pExtend, (const char *)text_T) == 0) {
      fits_read_fits_header_(&fileNum, pNXhead, ppXHead);
      pTempN = pNXhead;
      pTempHead = *ppXHead;
   }

   /* From the header, read BITPIX and determine the number of data points */
   /* (from the extended header if it exists) */
   *pNData = fits_compute_ndata_(pNHead, ppHead);
   fits_get_card_ival_(pBitpix, label_bitpix, pNXhead, ppXHead);

   /* Read data */
   retval = fits_read_fits_data_(&fileNum, pBitpix, pNData, ppData);

   inoutput_close_file(fileNum);
   return retval;
}

/******************************************************************************/
/*
 * Write FITS format data.  Write the header as a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * The data follows is written as 32-bit reals.  If necessary, the
 * data is converted to that format first.
 *
 * Returned value is 0 unless not all of the data points are written,
 * in which case the difference is returned.  (Does not work!!!???  Values
 * returned from fwrite() are bizarre!)
 */

DSIZE fits_write_file_fits_r4_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   float ** ppData)
{
   int      bitpix = -32;
   DSIZE    retval;

   fits_data_to_r4_(pNHead, ppHead, pNData, (uchar **)ppData);
   retval = fits_write_file_fits_noscale_(pFileName, pNHead,
    ppHead, pNData, &bitpix, (uchar **)ppData);
   return retval;
}

/******************************************************************************/
/*
 * Write FITS format data.  Write the header as a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * The data follows is written as 16-bit integers.  If necessary, the
 * data is converted to that format first.
 *
 * Returned value is 0 unless not all of the data points are written,
 * in which case the difference is returned.  (Does not work!!!???  Values
 * returned from fwrite() are bizarre!)
 */

DSIZE fits_write_file_fits_i2_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   short int ** ppData)
{
   int      bitpix = 16;
   DSIZE    retval;

   fits_data_to_i2_(pNHead, ppHead, pNData, (uchar **)ppData);
   retval = fits_write_file_fits_noscale_(pFileName, pNHead,
    ppHead, pNData, &bitpix, (uchar **)ppData);
   return retval;
}

/******************************************************************************/
/*
 * Write FITS format data.  Write the header as a multiple of
 * 2880-byte blocks, with the last block containing an END card.
 * The data follows as either real values or as integer values
 * that should be scaled by the BZERO and BSCALE values.  The data
 * format is determined by the BITPIX card in the header.
 *
 * Returned value is 0 unless not all of the data points are written,
 * in which case the difference is returned.  (Does not work!!!???  Values
 * returned from fwrite() are bizarre!)
 */

DSIZE fits_write_file_fits_noscale_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   int   *  pBitpix,
   uchar ** ppData)
{
   int      fileNum;
   DSIZE    retval;
   char     pPrivW[] = "w\0";

   inoutput_open_file(&fileNum,pFileName, pPrivW);

   /* Write header */
   fits_write_fits_header_(&fileNum, pNHead, ppHead);

   /* Write data */
   retval = fits_write_fits_data_(&fileNum, pBitpix, pNData, ppData);

   inoutput_close_file(fileNum);
   return retval;
}

/******************************************************************************/
/*
 * Read data blocks from an open FITS file.
 * One contiguous area of memory is dynamically allocated.
 *
 * Returned value is 0 unless the FITS file contains fewer data points
 * than indicated in the header, in which case the difference is returned.
 */
DSIZE fits_read_fits_data_
  (int   *  pFilenum,
   int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      size;
   DSIZE    retval;

   /* Allocate the minimum number of 2880-byte blocks for the data */
   fits_create_fits_data_(pBitpix, pNData, ppData);

   /* Read the data until the number of data points or until the end
      of file is reached. */
   size = fits_size_from_bitpix_(pBitpix);
   retval = *pNData - (int)fread(*ppData, size, *pNData, pFILEfits[*pFilenum]);
#ifdef LITTLE_ENDIAN
   fits_byteswap(*pBitpix, *pNData, *ppData);
#endif

   return retval;
}

/******************************************************************************/
/*
 * Write data blocks to an open FITS file.
 *
 * Returned value is 0 unless not all of the data points are written,
 * in which case the difference is returned.  (Does not work!  Values
 * returned from fwrite() are bizarre!)
 */
DSIZE fits_write_fits_data_
  (int   *  pFilenum,
   int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      i;
   int      j;
   int      k;
   int      size;
   int      retval;

   /* Write the number of data points indicated */
   size = fits_size_from_bitpix_(pBitpix);
#ifdef LITTLE_ENDIAN
   fits_byteswap(*pBitpix, *pNData, *ppData);
#endif
   retval = *pNData - (int)fwrite(*ppData, size, *pNData, pFILEfits[*pFilenum]);
#ifdef LITTLE_ENDIAN
   fits_byteswap(*pBitpix, *pNData, *ppData);
#endif
 
   /* Write some zeros such that the data takes up an integral number
      of 2880 byte blocks */
   j = (ftell(pFILEfits[*pFilenum]) % 2880)/size ;
   if (j != 0) {
      k = 1;
      for (i=j; i<(2880/size); i++)
       fwrite(datum_zero, size, k, pFILEfits[*pFilenum]);
   }

   return retval;
}

/******************************************************************************/
/*
 * Read header blocks from an open FITS file.
 * Memory for new blocks are dynamically allocated when needed.
 */
void fits_read_fits_header_
  (int   *  pFilenum,
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   HSIZE    jCard;
   uchar    pCard[80];

   /* Read the header into memory until the END card */
   *pNHead = 0;
   while (fits_get_next_card_(pFilenum, pCard)) {
      /* Only include this card if it is not blank */
      if (strncmp((const char *)pCard, (const char *)card_empty, 80) != 0) {
         fits_add_card_(pCard, pNHead, ppHead);
      }
   }
   fits_add_card_(card_end, pNHead, ppHead);
 
   /* Finish reading to the end of the last header block (the one w/END) */
   /* ignoring, and in effect deleting, any header cards after the END card */
   jCard = (ftell(pFILEfits[*pFilenum]) % 2880)/80 ;
   if (jCard != 0) {
      for (iCard=jCard; iCard<=35; iCard++) {
         fits_get_next_card_(pFilenum, pCard);
      }
   }

   /* Delete all cards where the label is blank */
   fits_purge_blank_cards_(pNHead, ppHead);

   /* Add missing cards to the FITS header */
   fits_add_required_cards_(pNHead, ppHead);
}

/******************************************************************************/
/*
 * Skip header blocks from an open FITS file.
 * This is a modified version of fits_read_fits_header_().
 */
void fits_skip_header_
  (int   *  pFilenum)
{
   HSIZE    iCard;
   HSIZE    jCard;
   uchar    pCard[80];

   /* Read the header into memory until the END card */
   while (fits_get_next_card_(pFilenum, pCard));
 
   /* Finish reading to the end of the last header block (the one w/END) */
   jCard = (ftell(pFILEfits[*pFilenum]) % 2880)/80 ;
   if (jCard != 0) {
      for (iCard=jCard; iCard<=35; iCard++) {
         fits_get_next_card_(pFilenum, pCard);
      }
   }
}

/******************************************************************************/
/*
 * Add any cards to the header that are required by the FITS definition
 * but are missing.
 */
void fits_add_required_cards_
  (HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iAxis;
   int      numAxes;
   int      naxis;
   int      naxisX;
#if 0
   int      crpixX;
   float    crvalX;
   float    cdeltX;
#endif
   DSIZE *  pNaxis;
   uchar    pLabel_temp[9]; /* Must be long enough for 8 chars + NULL */

   if (fits_get_card_ival_(&naxis, label_naxis, pNHead, ppHead) == FALSE) {
      naxis = 0; /* default to no data axes */
      fits_change_card_ival_(&naxis, label_naxis, pNHead, ppHead);
   }

   fits_compute_axes_(pNHead, ppHead, &numAxes, &pNaxis);

   for (iAxis=0; iAxis < numAxes; iAxis++) {
      /* For each axis, be sure that a NAXISx, CRPIXx, CRVALx and CDELTx
       * card exists.  If one does not exist, then create it.
       * Create the labels for each axis for which to look as pLabel_temp.
       * Be certain to pad with spaces so that a NULL is not written.
       */

      sprintf((char *)pLabel_temp, "NAXIS%-3d", iAxis+1);
      if (fits_get_card_ival_(&naxisX, pLabel_temp, pNHead, ppHead) == FALSE) {
         naxisX = 1; /* default to 1 */
         fits_change_card_ival_(&naxisX, pLabel_temp, pNHead, ppHead);
         printf("Adding a card %s\n", pLabel_temp);
      }

#if 0
      sprintf(pLabel_temp, "CRPIX%-3d  ", iAxis+1);
      if (fits_get_card_ival_(&crpixX, pLabel_temp, pNHead, ppHead) == FALSE) {
         crpixX = 1; /* default to start numbering at the first pixel */
         fits_change_card_ival_(&crpixX, pLabel_temp, pNHead, ppHead);
         printf("Adding a card %s\n", pLabel_temp);
      }

      sprintf(pLabel_temp, "CRVAL%-3d  ", iAxis+1);
      if (fits_get_card_rval_(&crvalX, pLabel_temp, pNHead, ppHead) == FALSE) {
         crvalX = 0.0; /* default to the first pixel value to be zero */
         fits_change_card_rval_(&crvalX, pLabel_temp, pNHead, ppHead);
         printf("Adding a card %s\n", pLabel_temp);
      }

      sprintf(pLabel_temp, "CDELT%-3d  ", iAxis+1);
      if (fits_get_card_rval_(&cdeltX, pLabel_temp, pNHead, ppHead) == FALSE) {
         cdeltX = 1.0; /* default to spacing each pixel by a value of 1 */
         fits_change_card_rval_(&cdeltX, pLabel_temp, pNHead, ppHead);
         printf("Adding a card %s\n", pLabel_temp);
      }
#endif
   }

   /* Plug a memory leak - Chris Stoughton 19-Jan-1999 */
   fits_free_axes_(&numAxes, &pNaxis);
}

/******************************************************************************/
/*
 * Write header blocks to an open FITS file.
 */
void fits_write_fits_header_
  (int   *  pFilenum,
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iCard;
   int      jCard;
   uchar *  pHead = *ppHead;

   /* Write the number of header cards indicated */
   for (iCard=0; iCard < *pNHead; iCard++) {
      fits_put_next_card_(pFilenum, &pHead[iCard*80]);
   }
 
   /* Write some more blank cards such that the header takes up an
      integral number of 2880 byte blocks */
   jCard = (ftell(pFILEfits[*pFilenum]) % 2880)/80 ;
   if (jCard != 0) {
      for (iCard=jCard; iCard <= 35; iCard++) {
         fits_put_next_card_(pFilenum, card_empty);
      }
   }
}

/******************************************************************************/
/*
 * Create a FITS header that only contains an END card.
 * Memory for new blocks are dynamically allocated when needed.
 */
void fits_create_fits_header_
  (HSIZE *  pNHead,
   uchar ** ppHead)
{
   /* First dispose of any memory already allocated by ppHead. */
   fits_dispose_array_(ppHead);

   /* Create a header with only a SIMPLE and END card.
    * Note that an entire 2880 byte block will be created
    * by the call to fits_add_card_().
    */
   *pNHead = 0;
   fits_add_card_(card_end, pNHead, ppHead);
   fits_add_card_(card_simple, pNHead, ppHead);
}

/******************************************************************************/
/*
 * Copy a FITS header into a newly created array.  Dynamically allocate
 * memory for the new header.
 */
void fits_duplicate_fits_header_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   uchar ** ppHeadCopy)
{
   MEMSZ    memSize;
 
   /* Allocate the minimum number of 2880-byte blocks for the header */
   memSize = ((int)((80*(*pNHead)-1)/2880) + 1) * 2880;
   ccalloc_(&memSize, (void **)ppHeadCopy);

   /* Copy all of the header bytes verbatim */
   memmove((void *)(*ppHeadCopy), (const void *)(*ppHead), memSize);
}

/******************************************************************************/
/*
 * Copy a FITS data array of real*4 into a newly created array.
 */
void fits_duplicate_fits_data_r4_
  (DSIZE *  pNData,
   float ** ppData,
   float ** ppDataCopy)
{
   int      bitpix = -32;

   fits_duplicate_fits_data_(&bitpix, pNData, (uchar **)ppData,
    (uchar **)ppDataCopy);
}

/******************************************************************************/
/*
 * Copy a FITS data array into a newly created array.
 */
void fits_duplicate_fits_data_
  (int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData,
   uchar ** ppDataCopy)
{
   int      size;
   MEMSZ    memSize;
 
   /* Allocate the minimum number of 2880-byte blocks for the header */
   size = fits_size_from_bitpix_(pBitpix);
   memSize = ((int)((size*(*pNData)-1)/2880) + 1) * 2880;
   ccalloc_(&memSize, (void **)ppDataCopy);

   /* Copy all of the data bytes verbatim */
   memmove((void *)(*ppDataCopy), (const void *)(*ppData), memSize);
}

/******************************************************************************/
/*
 * Create a FITS data array of real*4 with the number of elements specified.
 * Memory for new blocks are dynamically allocated when needed.
 */
void fits_create_fits_data_r4_
  (DSIZE *  pNData,
   float ** ppData)
{
   int      bitpix = -32;
   fits_create_fits_data_(&bitpix, pNData, (uchar **)ppData);
}

/******************************************************************************/
/*
 * Create a FITS data array with the number of elements specified.
 * Memory for new blocks are dynamically allocated when needed.
 */
void fits_create_fits_data_
  (int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      size;
   MEMSZ    memSize;

   /* Allocate the minimum number of 2880-byte blocks for the data */
   size = fits_size_from_bitpix_(pBitpix);
   memSize = ((int)((size*(*pNData)-1)/2880) + 1) * 2880;
   ccalloc_(&memSize, (void **)ppData);
}

/******************************************************************************/
/*
 * Free the memory allocated for the header and data arrays.
 * Return TRUE if both arrays existed and were freed, and FALSE otherwise.
 */
int fits_dispose_header_and_data_
  (uchar ** ppHead,
   uchar ** ppData)
{
   int      retval;

   retval = fits_dispose_array_(ppHead) && fits_dispose_array_(ppData);
   return retval;
}

/******************************************************************************/
/*
 * Free the memory allocated for a FITS header or data array.
 * Return TRUE if the array existed and was freed, and FALSE otherwise.
 */
int fits_dispose_array_
  (uchar ** ppHeadOrData)
{
   int      retval;

   retval = FALSE;
   if (*ppHeadOrData != NULL) {
      ccfree_((void **)ppHeadOrData);
      retval = TRUE;
   }
   return retval;
}

/******************************************************************************/
/*
 * Compute the total number of data points.
 * This information is determined from the header cards NAXIS and NAXISx.
 */
DSIZE fits_compute_ndata_
  (HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      numAxes;
   DSIZE    iAxis;
   DSIZE *  pNaxis;
   DSIZE    nData;

   fits_compute_axes_(pNHead, ppHead, &numAxes, &pNaxis);
   if (numAxes == 0)
      nData = 0;
   else {
      nData = 1;
      for (iAxis=0; iAxis < numAxes; iAxis++) nData *= pNaxis[iAxis];
   }

   /* Plug a memory leak - D. Schlegel 06-Feb-1999 */
   fits_free_axes_(&numAxes, &pNaxis);

   return nData;
}

/******************************************************************************/
/*
 * Compute the number of axes and the dimension of each axis.
 * This information is determined from the header cards NAXIS and NAXISx.
 */
void fits_compute_axes_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   int   *  pNumAxes,
   DSIZE ** ppNaxis)
{
   int      iAxis;
   int      ival;
   DSIZE *  pNaxis;
   MEMSZ    memSize;
   uchar    pLabel_temp[9];

   fits_get_card_ival_(pNumAxes, label_naxis, pNHead, ppHead);
   if (*pNumAxes > 0) {
      memSize = (*pNumAxes) * sizeof(DSIZE);
      ccalloc_(&memSize, (void **)ppNaxis);
      pNaxis = *ppNaxis;
      for (iAxis=0; iAxis < *pNumAxes; iAxis++) {
         /* Create the label for this axis for which to look.
          * Be certain to pad with spaces so that a NULL is not written.
          */
         sprintf((char *)pLabel_temp, "NAXIS%d  ", iAxis+1);
         fits_get_card_ival_(&ival, pLabel_temp, pNHead, ppHead);
         pNaxis[iAxis] = ival;
      }
   }
}
       
/******************************************************************************/
/*
 * Free memory for axes dimensions allocated by "fits_compute_axes_".
 */
void fits_free_axes_
  (int   *  pNumAxes,
   DSIZE ** ppNaxis)
{
   if (*pNumAxes > 0) {
      ccfree_((void **)ppNaxis);
   }
}

/******************************************************************************/
/*
 * Compute the wavelength for a given pixel number using Vista coefficients.
 * This must be preceded with a call to fits_compute_vista_poly_coeffs_
 * to find the polynomial coefficients from the header cards.
 * The first element of pCoeff is a central pixel number for the fit
 * and the remaining LAMORD elements are the polynomial coefficients.
 * The wavelength of pixel number iPix (zero-indexed):
 *   wavelength(iPix) = SUM{j=1,nCoeff-1} Coeff(j) * [iPix - Coeff(0)]**(j-1)
 */
float compute_vista_wavelength_
  (DSIZE *  pPixelNumber,
   int   *  pNCoeff,
   float ** ppCoeff)
{
   int      iCoeff;
   DSIZE    centralPixelNumber;
   float    wavelength;

   centralPixelNumber = (*ppCoeff)[0];
   wavelength = 0.0;
   for (iCoeff=1; iCoeff < *pNCoeff; iCoeff++) {
      wavelength += (*ppCoeff)[iCoeff]
       * pow(*pPixelNumber - centralPixelNumber, (float)(iCoeff-1));
   }
   return wavelength;
}

/******************************************************************************/
/*
 * Compute the number of coefficients for a polynomial wavelength fit
 * and the values of those coefficients.
 * This information is determined from the header cards LAMORD and LPOLYx.
 * Set nCoeff=LAMORD+1, and an array ppCoeff is created that has LAMORD+1
 * elements.  The first element is a central pixel number for the fit
 * and the remaining LAMORD elements are the polynomial coefficients.
 * The wavelength of pixel number iPix (zero-indexed):
 *   wavelength(iPix) = SUM{j=1,nCoeff-1} Coeff(j) * [iPix - Coeff(0)]**(j-1)
 * The coefficients are stored 4 on a line, so that the LPOLY0 card
 * contains up to the first 4 coefficients, and LPOLY1 up to the next 4, etc.
 */
void fits_compute_vista_poly_coeffs_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   int   *  pNCoeff,
   float ** ppCoeff)
{
   int      iCoeff;
   int      iLpolyNum;
   int      nLpolyNum;
   MEMSZ    memSize;
   uchar    pLabel_temp[9]; /* Must be long enough for 8 chars + NULL */
   char  *  pStringVal;
   char  *  pCardLoc;
   const char pCharSpace[] = " \'";

   fits_get_card_ival_(pNCoeff,label_lamord,pNHead,ppHead);
   if (*pNCoeff > 0) {
      (*pNCoeff)++;
      memSize = (*pNCoeff) * sizeof(float);
      ccalloc_(&memSize, (void **)ppCoeff);
      nLpolyNum = (*pNCoeff+3) / 4;
      iCoeff = 0;
      for (iLpolyNum=0; iLpolyNum < nLpolyNum; iLpolyNum++) {
         /* Create the label for this coefficient for which to look.
          * Be certain to pad with spaces so that a NULL is not written.
          */
         sprintf((char *)pLabel_temp, "LPOLY%-3d  ", iLpolyNum);
         fits_get_card_string_(&pStringVal, pLabel_temp, pNHead, ppHead);
         pCardLoc = pStringVal;
         for (iCoeff=iLpolyNum*4; iCoeff < min(iLpolyNum*4+4, *pNCoeff);
          iCoeff++) {
            sscanf(strtok(pCardLoc,pCharSpace), "%f", &(*ppCoeff)[iCoeff]);
            pCardLoc=NULL;
         }
      }
   }
}
       
/******************************************************************************/
/* 
 * Convert a data array to real*4 data, if it is not already.
 * A new array is created for the data, and the old array is discarded.
 * Change the BITPIX card in the header to -32 to indicate the data is real*4.
 */
void fits_data_to_r4_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      bitpix;
   int      newBitpix;
   DSIZE    iData;
   HSIZE    iCard;
   MEMSZ    memSize;
   float    bscale;
   float    bzero;
   float    blankval;
   float    newBlankval;
   float *  pNewData;

   fits_get_card_ival_(&bitpix, label_bitpix, pNHead, ppHead);

   /* Convert data to real*4 if not already */
   if (bitpix != -32) {

      /* Get the scaling parameters from the header */
      if (fits_get_card_rval_(&bscale, (uchar *)Label_bscale, pNHead, ppHead)
       == FALSE) {
         bscale = 1.0;  /* Default value for BSCALE */
      }
      if (fits_get_card_rval_(&bzero , (uchar *)Label_bzero , pNHead, ppHead)
       == FALSE) {
         bzero = 0.0;  /* Default value for BZERO */
      }

      /* Allocate the minimum number of 2880-byte blocks for the data */
      memSize = ((int)((4*(*pNData)-1)/2880) + 1) * 2880;
      ccalloc_(&memSize, (void **)&pNewData);

      /* Convert the data and write to the new array */
      /* Note that nothing is done to rescale BLANK values properly */
      for (iData=0; iData < *pNData; iData++) {
         pNewData[iData] =
          fits_get_rval_(&iData, &bitpix, &bscale, &bzero, ppData);
      }

      /* Free the memory from the old array, and change the ppData pointer
         to point to the new array */
      ccfree_((void **)ppData);
      *ppData = (uchar *)pNewData;

      /* Change the BITPIX card to -32, indicating the data is real*4 */
      newBitpix = -32;
      fits_change_card_ival_(&newBitpix, label_bitpix, pNHead, ppHead);

      /* Delete the BSCALE and BZERO cards which are no longer used */
      fits_delete_card_(label_bscale, pNHead, ppHead);
      fits_delete_card_(label_bzero , pNHead, ppHead);

      /* Rescale the BLANK card if it exists */
      if ((iCard = fits_find_card_(label_blank, pNHead, ppHead)) != *pNHead) {
         fits_get_card_rval_(&blankval, label_blank, pNHead, ppHead);
         if      (bitpix ==  8) newBlankval = blankval * bscale + bzero;
         else if (bitpix == 16) newBlankval = blankval * bscale + bzero;
         else if (bitpix == 32) newBlankval = blankval * bscale + bzero;
         else if (bitpix == -8) newBlankval = blankval;
         else if (bitpix ==-32) newBlankval = blankval;
         else if (bitpix ==-64) newBlankval = blankval;
         fits_change_card_rval_(&newBlankval, label_blank, pNHead, ppHead);
      }

   }
}

/******************************************************************************/
/* 
 * Convert a data array to integer*2 data, if it is not already.
 * A new array is created for the data, and the old array is discarded.
 * Change the BITPIX card in the header to 16 to indicate the data is integer*2.
 */
void fits_data_to_i2_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      bitpix;
   int      newBitpix;
   DSIZE    iData;
   HSIZE    iCard;
   MEMSZ    memSize;
   float    bscale;
   float    bzero;
   float    blankval;
   float    newBlankval;
   short int *  pNewData;

   fits_get_card_ival_(&bitpix, label_bitpix, pNHead, ppHead);

   /* Convert data to integer*2 if not already */
   if (bitpix != 16) {

      /* Get the scaling parameters from the header */
      if (fits_get_card_rval_(&bscale, (uchar *)Label_bscale, pNHead, ppHead)
       == FALSE) {
         bscale = 1.0;  /* Default value for BSCALE */
      }
      if (fits_get_card_rval_(&bzero , (uchar *)Label_bzero , pNHead, ppHead)
       == FALSE) {
         bzero = 0.0;  /* Default value for BZERO */
      }

      /* Allocate the minimum number of 2880-byte blocks for the data */
      memSize = ((int)((2*(*pNData)-1)/2880) + 1) * 2880;
      ccalloc_(&memSize, (void **)&pNewData);

      /* Convert the data and write to the new array */
      /* Note that nothing is done to rescale BLANK values properly */
      for (iData=0; iData < *pNData; iData++) {
         pNewData[iData] =
          fits_get_ival_(&iData, &bitpix, &bscale, &bzero, ppData);
      }

      /* Free the memory from the old array, and change the ppData pointer
         to point to the new array */
      ccfree_((void **)ppData);
      *ppData = (uchar *)pNewData;

      /* Change the BITPIX card to 16, indicating the data is integer*2 */
      newBitpix = 16;
      fits_change_card_ival_(&newBitpix, label_bitpix, pNHead, ppHead);

      /* Delete the BSCALE and BZERO cards which are no longer used */
      fits_delete_card_(label_bscale, pNHead, ppHead);
      fits_delete_card_(label_bzero , pNHead, ppHead);

      /* Rescale the BLANK card if it exists */
      if ((iCard = fits_find_card_(label_blank, pNHead, ppHead)) != *pNHead) {
         fits_get_card_rval_(&blankval, label_blank, pNHead, ppHead);
         if      (bitpix ==  8) newBlankval = blankval * bscale + bzero;
         else if (bitpix == 16) newBlankval = blankval * bscale + bzero;
         else if (bitpix == 32) newBlankval = blankval * bscale + bzero;
         else if (bitpix == -8) newBlankval = blankval;
         else if (bitpix ==-32) newBlankval = blankval;
         else if (bitpix ==-64) newBlankval = blankval;
         fits_change_card_rval_(&newBlankval, label_blank, pNHead, ppHead);
      }

   }
}

/******************************************************************************/
/*
 * Add a card immediately before the END card, or as the next card
 * (if no blank or END card), whichever comes first.  Return the card
 * number of the added card.
 * Memory is dynamically allocated if necessary by adding another 2880-byte
 * block.
 */
HSIZE fits_add_card_
  (uchar    pCard[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    numCardEnd;
   MEMSZ    memSize;
   uchar    pCardTemp[80];
   uchar *  pNewHeader;

   fits_string_to_card_(pCard, pCardTemp);

   numCardEnd=fits_find_card_(card_end, pNHead, ppHead);

   /* Test to see if more memory is needed for the header */
   if ((*pNHead)%36 == 0) {
      /* Copy header to new location and change appropriate pointers */
      memSize = (36+(*pNHead)) * 80;
      ccalloc_(&memSize, (void **)&pNewHeader);
      if (*pNHead > 0) {
         memmove(pNewHeader, *ppHead, (*pNHead)*80);
         ccfree_((void **)ppHead);
      }
      *ppHead = pNewHeader;
      numCardEnd += (pNewHeader - *ppHead);
   }

   if ((*pNHead > 0) && (numCardEnd<*pNHead) ) {
      /* Copy the end card forward 80 bytes in memory */
      memmove(&(*ppHead)[(numCardEnd+1)*80], &(*ppHead)[numCardEnd*80], 80);
      /* Add the new card where the END card had been */
      memmove(&(*ppHead)[numCardEnd*80], pCardTemp, 80);
      (*pNHead)++;
      return numCardEnd;
   }
   else {
      /* There is no end card, so simply add the new card at end of header */
      memmove(&(*ppHead)[(*pNHead)*80], pCardTemp, 80);
      return (*pNHead)++;
   }
}

/******************************************************************************/
/*
 * Add a card in the first card with a blank label or immediately before
 * the END card, or as the next card (if no blank or END card), whichever
 * comes first.  Return the card number of the added card.
 * Memory is dynamically allocated if necessary.
 */
HSIZE fits_add_cardblank_
  (uchar    pCard[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    numCardEmpty;
   HSIZE    numCardEnd;
   MEMSZ    memSize;
   uchar *  pHead = *ppHead;
   uchar *  pNewHeader;

   numCardEmpty = fits_find_card_(card_empty, pNHead, ppHead);
   numCardEnd   = fits_find_card_(card_end  , pNHead, ppHead);

   /* First case finds a blank card before the end card that is overwritten  */
   if ((*pNHead > 0) && (numCardEmpty < numCardEnd)) {
      memmove(&pHead[numCardEmpty*80], pCard, 80);
      return numCardEmpty;
   }
   else {
      /* Test to see if more memory is needed for the header */
      if ((*pNHead)%36 == 0) {
         /* Copy header to new location and change appropriate pointers */
         memSize = (36+(*pNHead)) * 80;
         ccalloc_(&memSize, (void **)&pNewHeader);
         memmove(pNewHeader, pHead, (*pNHead)*80);
         ccfree_((void **)&pHead);
         pHead = pNewHeader;
         numCardEmpty += (pNewHeader-pHead);
         numCardEnd   += (pNewHeader-pHead);
      }
      if ((*pNHead > 0) && (numCardEnd < *pNHead) ) {
         /* Copy the end card forward 80 bytes in memory */
         memmove(&pHead[(numCardEnd+1)*80], &pHead[numCardEnd*80], 80);
         /* Add the new card where the END card had been */
         memmove(&pHead[numCardEnd*80], pCard, 80);
         (*pNHead)++;
         return numCardEnd;
      } else {
         /* There is no end card, so simply add the new card at end of header */
         memmove(&pHead[(*pNHead)*80], pCard, 80);
         return (*pNHead)++;
      }
   }
}

/******************************************************************************/
/*
 * Create a new card with the given label and integer value.
 * Note that this can create multiple cards with the same label.
 * Return the card number of the new card.
 */
HSIZE fits_add_card_ival_
  (int   *  pIval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   sprintf((char *)pCardTemp, "%-8.8s= %20d", pLabel, *pIval);
   iCard = fits_add_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Create a new card with the given label and real value.
 * Note that this can create multiple cards with the same label.
 * Return the card number of the new card.
 */
HSIZE fits_add_card_rval_
  (float *  pRval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   sprintf((char *)pCardTemp, "%-8.8s= %20.7e", pLabel, *pRval);
   iCard = fits_add_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Create a new card with the given label and string value.
 * Note that this can create multiple cards with the same label.
 * Return the card number of the new card.
 */
HSIZE fits_add_card_string_
  (char  *  pStringVal,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   /* !!!??? NOTE: A QUOTE SHOULD BE WRITTEN AS 2 SINGLE QUOTES */
   sprintf((char *)pCardTemp, "%-8.8s= '%-1.68s'", pLabel, pStringVal);
   iCard = fits_add_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Create a new COMMENT card with the given string.
 * Note that this can create multiple cards with the same label.
 * Return the card number of the new card.
 */
HSIZE fits_add_card_comment_
  (char  *  pStringVal,
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   /* !!!??? NOTE: A QUOTE SHOULD BE WRITTEN AS 2 SINGLE QUOTES */
   sprintf((char *)pCardTemp, "COMMENT %-1.72s", pStringVal);
   iCard = fits_add_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Create a new HISTORY card with the given string.
 * Note that this can create multiple cards with the same label.
 * Return the card number of the new card.
 */
HSIZE fits_add_card_history_
  (char  *  pStringVal,
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   /* !!!??? NOTE: A QUOTE SHOULD BE WRITTEN AS 2 SINGLE QUOTES */
   sprintf((char *)pCardTemp, "HISTORY %-1.72s", pStringVal);
   iCard = fits_add_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Delete all cards where the label is blank.
 * Return the number of cards that were discarded.
 */
HSIZE fits_purge_blank_cards_
  (HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    numDelete;

   numDelete = 0;
   while (fits_delete_card_(label_empty, pNHead, ppHead) != *pNHead) {
      numDelete++;
   }

   return numDelete;
}

/******************************************************************************/
/*
 * Delete the first card that matches the given label, or do nothing if no
 * matches are found.  Return the card number of the deleted card,
 * or return nHead (out of range) if no match was found.
 */
HSIZE fits_delete_card_
  (uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   HSIZE    jCard;
   uchar *  pHead = *ppHead;

   iCard = fits_find_card_(pLabel, pNHead, ppHead);
   if (iCard < *pNHead) {
      (*pNHead)--;
      for (jCard=iCard; jCard <* pNHead; jCard++) {
         memmove(&pHead[jCard*80], &pHead[(jCard+1)*80], 80);
      }
      memmove(&pHead[jCard*80], card_empty, 80);
   }
   return iCard;
}

/******************************************************************************/
/*
 * Return the card number of the 1st header card with the label passed,
 * or return nHead (out of range) if no match was found.
 */
HSIZE fits_find_card_
  (uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar *  pHead;

   if (*pNHead == 0) iCard=0;
   else {
      pHead = *ppHead;
      for (iCard=0;
       (iCard<*pNHead) && (strncmp(pLabel, &pHead[iCard*80],8)!=0); iCard++);
   }
   return iCard;
}

/******************************************************************************/
/* Swap the integer values in the cards that match the passed labels.
 */
void fits_swap_cards_ival_
  (uchar *  pLabel1,
   uchar *  pLabel2,
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      ival1;
   int      ival2;
 
   fits_get_card_ival_(&ival1, pLabel1, pNHead, ppHead);
   fits_get_card_ival_(&ival2, pLabel2, pNHead, ppHead);
   fits_change_card_ival_(&ival2, pLabel1, pNHead, ppHead);
   fits_change_card_ival_(&ival1, pLabel2, pNHead, ppHead);
}
 
/******************************************************************************/
/* Swap the integer values in the cards that match the passed labels.
 */
void fits_swap_cards_rval_
  (uchar *  pLabel1,
   uchar *  pLabel2,
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   float    rval1;
   float    rval2;
 
   fits_get_card_rval_(&rval1, pLabel1, pNHead, ppHead);
   fits_get_card_rval_(&rval2, pLabel2, pNHead, ppHead);
   fits_change_card_rval_(&rval2, pLabel1, pNHead, ppHead);
   fits_change_card_rval_(&rval1, pLabel2, pNHead, ppHead);
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and return the integer value of the argument after the label.
 * Return TRUE if there is a match, and FALSE if there is none.
 */
int fits_get_card_ival_
  (int   *  pIval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   HSIZE    iret;
   uchar *  pHead = *ppHead;
   char     pTemp[21];

   for (iCard=0;
    (iCard<*pNHead) && (strncmp(pLabel, &pHead[iCard*80], 8)!=0); iCard++);
   if (iCard < *pNHead) {
#if 0
     sscanf(&pHead[iCard*80+10], "%20d", pIval);
#endif
     memmove(pTemp, &pHead[iCard*80+10], 20);
     pTemp[20] = '\0';
     sscanf(pTemp, "%d", pIval);
     iret = TRUE;
   }
   else {
     iret = FALSE;
   }
   return iret;
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and return the real (float) value of the argument after the label.
 * Return TRUE if there is a match, and FALSE if there is none.
 */
int fits_get_card_rval_
  (float *  pRval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iCard;
   int      iret;
   uchar *  pHead = *ppHead;
   char     pTemp[21];

   for (iCard=0; (iCard<*pNHead) && (strncmp(pLabel, &pHead[iCard*80], 8)!=0);
    iCard++);
   if (iCard < *pNHead) {
#if 0
     sscanf(&pHead[iCard*80+10], "%20f", pRval);
#endif
     memmove(pTemp, &pHead[iCard*80+10], 20);
     pTemp[20] = '\0';
     sscanf(pTemp, "%f", pRval);
     iret = TRUE;
   }
   else {
     iret = FALSE;
   }
   return iret;
}

#if 0
/******************************************************************************/
/*
 * Return TRUE if there is a match, and FALSE if there is none.
 */
int fits_get_julian_date_
  (float *  pJulianDate,
   uchar    pLabelDate[],
   uchar    pLabelTime[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iret;
   int      month;
   int      date;
   int      year;
   float    time;

   if (iret=fits_get_card_date_(month,date,year,pLabelDate,pNHead,ppHead)
    == TRUE) {
      *pJulianDate=...
      if (fits_get_card_time_(&time,pLabelTime,pNHead,ppHead) == TRUE) {
         *pJulianDate+=...
      }
   } else {
      *pJulianDate=0.0;
   }
   return iret;
}
#endif

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and return the date as three integers month, date and year.
 * Return TRUE if there is a match, and FALSE if there is none.
 */
int fits_get_card_date_
  (int   *  pMonth,
   int   *  pDate,
   int   *  pYear,
   uchar    pLabelDate[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iret;
   char  *  pStringVal;

   iret = fits_get_card_string_(&pStringVal, pLabelDate, pNHead, ppHead);
   if (iret == TRUE) {
      sscanf(pStringVal, "%d/%d/%d", pMonth, pDate, pYear);
      if (*pYear < 1900) *pYear += 1900;
      /* Free the memory used for the string value of this card */
      ccfree_((void **)&pStringVal);
   }
   return iret;
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and return the time (TIME, RA, DEC or HA, for example) converted
 * to a real value.  Typically, this is used with TIME, RA or HA
 * to return a value in hours, or it is used with DEC to return a
 * value in degrees.
 * Return TRUE if there is a match, and FALSE if there is none.
 */
int fits_get_card_time_
  (float *  pTime,
   uchar    pLabelTime[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iret;
   int      timeHour;
   int      timeMin;
   float    timeSec;
   char  *  pStringVal;

   iret = fits_get_card_string_(&pStringVal, pLabelTime, pNHead, ppHead);
   if (iret == TRUE) {
      sscanf(pStringVal, "%d:%d:%f", &timeHour, &timeMin, &timeSec);
      *pTime=abs(timeHour) + timeMin/60.0 + timeSec/3600.0;
      /* Make the returned value negative if a minus sign is in the string */
      if (strchr(pStringVal, '-') != NULL) *pTime=-(*pTime);
      /* Free the memory used for the string value of this card */
      ccfree_((void **)&pStringVal);
   } else {
      *pTime = 0.0;
   }
   return iret;
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and return a pointer to the string argument after the label.
 * Memory is dynamically allocated for the string argument.
 * Return TRUE if there is a match, and FALSE if there is none.
 * If there is not match, then create and return the string pStringUnknown.
 */
int fits_get_card_string_
  (char  ** ppStringVal,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   int      iChar;
   int      iret;
   HSIZE    iCard;
   MEMSZ    memSize;
   uchar *  pHead = *ppHead;
   char  *  pTemp;
   char     pStringUnknown[] = "?";

   memSize = 70;
   ccalloc_(&memSize, (void **)&pTemp);
   for (iCard=0;
    (iCard<*pNHead) && (strncmp(pLabel, &pHead[iCard*80], 8)!=0); iCard++);
   if (iCard < *pNHead) {
   /* It must start with a single quote in column 11 (1-indexed) if not blank.
      Otherwise, an empty string is returned, which is O.K. */
     iChar = 11;
     /* Copy characters from column 12 until column 80 or another single
        quote is reached. */
     /* !!!??? NOTE: TWO SINGLE QUOTES SHOULD BE READ IN AS A QUOTE */
     if (pHead[iCard*80+10]=='\'') {
       while (iChar<80 && (pTemp[iChar-11]=pHead[iCard*80+iChar]) != '\'')
        iChar++;
     }

     pTemp[iChar-11]='\0';  /* Pad with a NULL at the end of the string */
     /* Remove trailing blanks; leading blanks are significant */
     iChar = strlen(pTemp);
     while (iChar>0 && pTemp[--iChar]==' ') pTemp[iChar]='\0';

     iret = TRUE;
   }
   else {
     strcpy(pTemp, pStringUnknown);

     iret = FALSE;
   }

   *ppStringVal=pTemp;
   return iret;
}

/******************************************************************************/
/*
 * Change the 1st card that matches the passed label, or add a card if there
 * is not a match.  Return the card number of the changed or added card.
 */
HSIZE fits_change_card_
  (uchar    pCard[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[80];
   uchar *  pHead = *ppHead;

   fits_string_to_card_(pCard, pCardTemp);

   iCard = fits_find_card_(pCardTemp, pNHead, ppHead);
   if (iCard < *pNHead) {
      memmove(&pHead[iCard*80], pCardTemp, 80);
   } else {
      iCard = fits_add_card_(pCardTemp, pNHead, ppHead);
   }

   return iCard;
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and change the integer value of the argument after the label.
 * If no card exists, then create one.  Return the card number of
 * the changed or added card.
 */
HSIZE fits_change_card_ival_
  (int   *  pIval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   sprintf(pCardTemp, "%-8.8s= %20d", pLabel, *pIval);
   iCard = fits_change_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and change the real (float) value of the argument after the label.
 * If no card exists, then create one.  Return the card number of
 * the changed or added card.
 */
HSIZE fits_change_card_rval_
  (float *  pRval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   sprintf(pCardTemp, "%-8.8s= %20.7e", pLabel, *pRval);
   iCard = fits_change_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/*
 * Find the 1st header card whose label matches the label passed,
 * and change the string value of the argument after the label.
 * If no card exists, then create one.  Return the card number of
 * the changed or added card.
 */
HSIZE fits_change_card_string_
  (char  *  pStringVal,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead)
{
   HSIZE    iCard;
   uchar    pCardTemp[81]; /* Last character is for null from sprintf() */

   /* !!!??? NOTE: A QUOTE SHOULD BE WRITTEN AS 2 SINGLE QUOTES */
   sprintf(pCardTemp, "%-8.8s= '%-1.68s'", pLabel, pStringVal);
   iCard = fits_change_card_(pCardTemp, pNHead, ppHead);

   return iCard;
}

/******************************************************************************/
/* Convert a character string to a FITS-complient 80-character card.
 * The string is copied until either a NULL or CR is reached or the 80th
 * character is reached.  The remainder of the card is padded with spaces.
 * In addition, the label part of the card (the first 8 characters)
 * are converted to upper case.
 *
 * Note that pCard[] must be dimensioned to at least the necessary 80
 * characters.
 */
void fits_string_to_card_
  (uchar    pString[],
   uchar    pCard[])
{
   int      iChar;
   int      qNull;

   /* Copy the raw string into the card array */
   memmove(pCard, pString, 80);

   /* Search for a NULL or CR in the card, and replace that character and
    * all following characters with a space.
    */
   qNull = FALSE;
   iChar = 0;
   while (iChar < 80) {
      if (pCard[iChar] == '\0' || pCard[iChar] == '\n') qNull = TRUE;
      if (qNull == TRUE) pCard[iChar] = ' ';
      iChar++;
   }

   /* Convert the label (the first 8 characters) to upper case) */
   for (iChar=0; iChar < 8; iChar++) {
      pCard[iChar] = toupper(pCard[iChar]);
   }
}

/******************************************************************************/
/*
 * Return the (float) value of the data array indexed by the iloc'th elements,
 * taking care to use the proper data format as specified by bitpix.
 * Several unconventional values for bitpix are supported: 32, 8, -8.
 * For a 2-dimensional array, set iloc=x+y*naxis1.
 */
float fits_get_rval_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBscale,
   float *  pBzero,
   uchar ** ppData)
{
   float    rval;
   uchar     * pIdata8  = (uchar     *)(*ppData);
   short int * pIdata16 = (short int *)(*ppData);
   long  int * pIdata32 = (long  int *)(*ppData);
   float     * pRdata32 = (float     *)(*ppData);
   double    * pRdata64 = (double    *)(*ppData);

   if      (*pBitpix ==-32) rval = pRdata32[*pIloc];
   else if (*pBitpix == 16) rval = pIdata16[*pIloc] * (*pBscale) + (*pBzero);
   else if (*pBitpix == 32) rval = pIdata32[*pIloc] * (*pBscale) + (*pBzero);
   else if (*pBitpix ==-64) rval = pRdata64[*pIloc];
   else if (*pBitpix ==  8) rval = pIdata8 [*pIloc] * (*pBscale) + (*pBzero);
   else if (*pBitpix == -8) rval = pIdata8 [*pIloc];
   else                     rval = 0.0; /* Invalid BITPIX! */
   return rval;
}

/******************************************************************************/
/*
 * Return the (int) value of the data array indexed by the iloc'th elements,
 * taking care to use the proper data format as specified by bitpix.
 * Several unconventional values for bitpix are supported: 32, 8, -8.
 * For a 2-dimensional array, set iloc=x+y*naxis1.
 */
int fits_get_ival_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBscale,
   float *  pBzero,
   uchar ** ppData)
{
   int      ival;
   float    rval;
   uchar     * pIdata8  = (uchar     *)(*ppData);
   short int * pIdata16 = (short int *)(*ppData);
   long  int * pIdata32 = (long  int *)(*ppData);
   float     * pRdata32 = (float     *)(*ppData);
   double    * pRdata64 = (double    *)(*ppData);

   if      (*pBitpix ==-32) rval = pRdata32[*pIloc];
   else if (*pBitpix == 16) rval = pIdata16[*pIloc] * (*pBscale) + (*pBzero);
   else if (*pBitpix == 32) rval = pIdata32[*pIloc] * (*pBscale) + (*pBzero);
   else if (*pBitpix ==-64) rval = pRdata64[*pIloc];
   else if (*pBitpix ==  8) rval = pIdata8 [*pIloc] * (*pBscale) + (*pBzero);
   else if (*pBitpix == -8) rval = pIdata8 [*pIloc];
   else                     rval = 0.0; /* Invalid BITPIX! */

   /* Round to the nearest integer */
   if (rval >= 0.0) {
      ival = rval + 0.5;
   } else {
      ival = rval - 0.5;
   }

   return ival;
}

/******************************************************************************/
/*
 * Put a (float) value into location iloc of the data array, taking care to
 * use the proper data format as specified by bitpix.  For a 2-dimensional
 * array, set iloc=x+y*naxis1.
 * Several unconventional values for bitpix are supported: 32, 8, -8.
 * Note: Is the rounding done properly!!!???
 */
void fits_put_rval_
  (float *  pRval,
   DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBscale,
   float *  pBzero,
   uchar ** ppData)
{
   uchar     * pIdata8  = (uchar     *)(*ppData);
   short int * pIdata16 = (short int *)(*ppData);
   long  int * pIdata32 = (long  int *)(*ppData);
   float     * pRdata32 = (float     *)(*ppData);
   double    * pRdata64 = (double    *)(*ppData);

   if      (*pBitpix ==-32) pRdata32[*pIloc] = *pRval;
   else if (*pBitpix == 16) pIdata16[*pIloc] = (*pRval - *pBzero) / (*pBscale);
   else if (*pBitpix == 32) pIdata32[*pIloc] = (*pRval - *pBzero) / (*pBscale);
   else if (*pBitpix ==-64) pRdata64[*pIloc] = *pRval;
   else if (*pBitpix ==  8) pIdata8 [*pIloc] = (*pRval - *pBzero) / (*pBscale);
   else if (*pBitpix == -8) pIdata8 [*pIloc] = *pRval;
}

/******************************************************************************/
/*
 * Ask whether a particular pixel position in the data array is equal
 * to the value specified by the BLANK card.  This test is performed WITHOUT
 * first rescaling the data.  Pass the blank value as
 * a real variable, even if it was originally integer.  For a 2-dimensional
 * array, set iloc=x+y*naxis1.  Return TRUE (iq!=0) if the pixel is
 * BLANK, or FALSE (iq==0) if it is not.
 * The value blankval must be found first and passed to this routine.
 * Several unconventional values for bitpix are supported: 32, 8, -8.
 */
int fits_qblankval_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBlankval,
   uchar ** ppData)
{
   int      iq;
   uchar     * pIdata8  = (uchar     *)(*ppData);
   short int * pIdata16 = (short int *)(*ppData);
   long  int * pIdata32 = (long  int *)(*ppData);
   float     * pRdata32 = (float     *)(*ppData);
   double    * pRdata64 = (double    *)(*ppData);

   if      (*pBitpix ==-32) iq = ( pRdata32[*pIloc] == (*pBlankval) );
   else if (*pBitpix == 16) iq = ( pIdata16[*pIloc] == (*pBlankval) );
   else if (*pBitpix == 32) iq = ( pIdata32[*pIloc] == (*pBlankval) );
   else if (*pBitpix ==-64) iq = ( pRdata64[*pIloc] == (*pBlankval) );
   else if (*pBitpix ==  8) iq = ( pIdata8 [*pIloc] == (*pBlankval) );
   else if (*pBitpix == -8) iq = ( pIdata8 [*pIloc] == (*pBlankval) );
   else                     iq = FALSE; /* Invalid BITPIX! */

   return iq;
}

/******************************************************************************/
/*
 * Replace a data element by a BLANK value as determined by blankval.
 * The value is assigned WITHOUT rescaling.
 * The value blankval must be found first and passed to this routine.
 * Several unconventional values for bitpix are supported: 32, 8, -8.
 */
void fits_put_blankval_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBlankval,
   uchar ** ppData)
{
   uchar     * pIdata8  = (uchar     *)(*ppData);
   short int * pIdata16 = (short int *)(*ppData);
   long  int * pIdata32 = (long  int *)(*ppData);
   float     * pRdata32 = (float     *)(*ppData);
   double    * pRdata64 = (double    *)(*ppData);

   if      (*pBitpix ==-32) pRdata32[*pIloc] = *pBlankval;
   else if (*pBitpix == 16) pIdata16[*pIloc] = *pBlankval;
   else if (*pBitpix == 32) pIdata32[*pIloc] = *pBlankval;
   else if (*pBitpix ==-64) pRdata64[*pIloc] = *pBlankval;
   else if (*pBitpix ==  8) pIdata8 [*pIloc] = *pBlankval;
   else if (*pBitpix == -8) pIdata8 [*pIloc] = *pBlankval;
}

/******************************************************************************/
/*
 * Replace any nulls in a card by spaces.
 */
void fits_purge_nulls
  (uchar    pCard[])
{
   int iChar;

   for (iChar=0; iChar < 80; iChar++) {
      if (pCard[iChar] == '\0') pCard[iChar] = ' ';
   }
}

/******************************************************************************/
/*
 * Read the next 80-character card from the specified device.
 * Return 0 if the END card is reached.
 */
int fits_get_next_card_
  (int   *  pFilenum,
   uchar    pCard[])
{
   int      iChar;

   for (iChar=0; iChar < 80; iChar++) {
      pCard[iChar] = fgetc(pFILEfits[*pFilenum]);
   }
   return strncmp((const char *)card_end, (const char *)pCard, 8);
}

/******************************************************************************/
/*
 * Write passed card to open file.  Return FALSE for a write error.
 */
int fits_put_next_card_
  (int   *  pFilenum,
   uchar    pCard[])
{
   int      iChar;
   int      retval;

   retval = TRUE;
   for (iChar=0; iChar < 80; iChar++) {
      if (fputc(pCard[iChar], pFILEfits[*pFilenum]) == EOF) retval = FALSE;
   }
   return retval;
}

/******************************************************************************/
/*
 * Determine the size of an individual datum based upon the FITS definitions
 * of the BITPIX card.
 */
int fits_size_from_bitpix_
  (int *pBitpix)
{
   int size;

   if      (*pBitpix ==   8) size = 1;
   else if (*pBitpix ==  16) size = 2;
   else if (*pBitpix ==  32) size = 4;
   else if (*pBitpix ==  64) size = 8;
   else if (*pBitpix == -16) size = 2;
   else if (*pBitpix == -32) size = 4;
   else if (*pBitpix == -64) size = 8;
   else                      size = 0; /* Bitpix undefined! */

   return size;
}

/******************************************************************************/
/*
 * For data of arbitrary dimensions, shift the pixels along the "*pSAxis"
 * axis by "*pShift" pixels, wrapping data around the image boundaries.
 * For example, if the middle dimension of a 3-dimen array is shifted:
 *   new[i,j+shift,k] = old[i,j,k]
 * The data can be of any data type (i.e., any BITPIX).
 */
void fits_pixshift_wrap_
  (int   *  pSAxis,
   DSIZE *  pShift,
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      size;
   DSIZE    posShift;
   int      iAxis;
   int      numAxes;
   DSIZE *  pNaxis;
   DSIZE    dimBig;
   DSIZE    dimSml;
   DSIZE    indxBig;
   DSIZE    indxSml;
   DSIZE    offset;
   DSIZE    iloc;
   int      bitpix;
   MEMSZ    memSize;
   DSIZE    nVector;
   DSIZE    iVector;
   uchar *  pVector;

   fits_compute_axes_(pNHead, ppHead, &numAxes, &pNaxis);
   nVector = pNaxis[*pSAxis];
   posShift = *pShift;
   while (posShift < 0) posShift += nVector; /* Must be positive value */

   /* Allocate an array equal in size to one vector in the *pSAxis dimension */
   fits_get_card_ival_(&bitpix, label_bitpix, pNHead, ppHead);
   size = fits_size_from_bitpix_(&bitpix);
   memSize = size * nVector;
   ccalloc_(&memSize, (void **)&pVector);

   /* Compute the number of larger and smaller indices */
   dimBig = 1;
   for (iAxis=0; iAxis < *pSAxis; iAxis++) dimBig *= pNaxis[iAxis];
   dimSml = 1;
   for (iAxis=*pSAxis+1; iAxis < numAxes; iAxis++) dimSml *= pNaxis[iAxis];

   /* Loop through each of the larger and smaller indices */
   for (indxBig=0; indxBig < dimBig; indxBig++) {
   for (indxSml=0; indxSml < dimSml; indxSml++) {
      offset = indxBig * nVector * dimSml + indxSml;

      /* Copy vector into temporary vector */
      for (iVector=0; iVector < nVector; iVector++) {
         iloc = offset + iVector * dimSml;
         memmove(&pVector[iVector*size], &(*ppData)[iloc*size], size);
      }

      /* Copy the shifted vector back into the main data array */
      for (iVector=0; iVector < nVector; iVector++) {
         /* Use the MOD operator below to wrap the dimensions */
         iloc = offset + ((iVector+(posShift)) % nVector) * dimSml;
         memmove(&(*ppData)[iloc*size], &pVector[iVector*size], size);
      }
   } }

   /* Free memory */
   ccfree_((void **)&pVector);

   /* Plug a memory leak - D. Schlegel 06-Feb-1999 */
   fits_free_axes_(&numAxes, &pNaxis);
}

/******************************************************************************/
/*
 * For data of 2 dimensions, transpose the data by setting
 * pData[i][j] = pData[j][i].
 * A new data array is created and the old one is destroyed.
 * Also, swap the appropriate header cards.
 */
void fits_transpose_data_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData)
{
   int      bitpix;
   int      size;
   int      iByte;
   int      numAxes;
   DSIZE *  pNaxis;
   DSIZE    nData;
   DSIZE    iRow;
   DSIZE    iCol;
   DSIZE    ilocOld;
   DSIZE    ilocNew;
   MEMSZ    memSize;
   uchar *  pNewData;

   fits_compute_axes_(pNHead, ppHead, &numAxes, &pNaxis);
   if (numAxes == 2) {
      /* Allocate an array equal in size to the data array */
      nData = fits_compute_ndata_(pNHead, ppHead);
      fits_get_card_ival_(&bitpix, label_bitpix, pNHead, ppHead);
      size = fits_size_from_bitpix_(&bitpix);
      memSize = size * nData;
      ccalloc_(&memSize, (void **)&pNewData);

      /* Copy the data into the new data array, transposing the first 2 axes */
      for (iRow=0; iRow < pNaxis[1]; iRow++) {
         for (iCol=0; iCol < pNaxis[0]; iCol++) {
            ilocOld = size * (iRow*pNaxis[0] + iCol);
            ilocNew = size * (iCol*pNaxis[1] + iRow);
            /* For each data element, copy the proper number of bytes */
            for (iByte=0; iByte < size; iByte++) {
               pNewData[ilocNew+iByte] = (*ppData)[ilocOld+iByte];
            }
         }
      }

      /* Discard the old data array and return the new one */
      ccfree_((void **)ppData);
      *ppData = pNewData;

      /* Switch the values in the header of NAXIS1 and NAXIS2,
       * and the cards used to label the pixel numbers on those axes.
       */
      fits_swap_cards_ival_(label_naxis1, label_naxis2, pNHead, ppHead);
      fits_swap_cards_rval_(label_crpix1, label_crpix2, pNHead, ppHead);
      fits_swap_cards_rval_(label_crval1, label_crval2, pNHead, ppHead);
      fits_swap_cards_rval_(label_cdelt1, label_cdelt2, pNHead, ppHead);
   }

   /* Plug a memory leak - D. Schlegel 06-Feb-1999 */
   fits_free_axes_(&numAxes, &pNaxis);
}

/******************************************************************************/
/*
 * Average several rows (or columns) of a 2-dimensional array of floats.
 * If (*iq)==0 then average rows; if (*iq)==1 then average columns.
 * Note that *pNaxis1=number of columns and *pNaxis2=number of rows.
 * Memory is dynamically allocated for the output vector.
 */
void fits_ave_rows_r4_
  (int   *  iq,
   DSIZE *  pRowStart,
   DSIZE *  pNumRowAve,
   DSIZE *  pNaxis1,
   DSIZE *  pNaxis2,
   float ** ppData,
   float ** ppOut)
{
   DSIZE   iCol;
   DSIZE   iRow;
   DSIZE   rowStart;
   DSIZE   rowEnd;
   MEMSZ   memSize;
   float   weight;
   float * pData = *ppData;
   float * pOut;

   if (*iq == 0) {
      memSize = sizeof(float) * (*pNaxis1);
      ccalloc_(&memSize, (void **)ppOut);
      pOut = *ppOut;
      rowStart = max(0, *pRowStart);
      rowEnd = min(*pRowStart + *pNumRowAve, *pNaxis2);
      weight = (rowEnd + 1 - rowStart);
      for (iCol=0; iCol < *pNaxis1; iCol++) {
         pOut[iCol] = 0.0;
         for (iRow=rowStart; iRow <= rowEnd; iRow++) {
            pOut[iCol] += pData[iRow*(*pNaxis1) + iCol];
         }
         pOut[iCol] /= weight;
      }
   } else if (*iq == 1) {
      memSize = sizeof(float) * (*pNaxis2);
      ccalloc_(&memSize, (void **)ppOut);
      pOut = *ppOut;
      rowStart = max(0, *pRowStart);
      rowEnd = min(*pRowStart + *pNumRowAve, *pNaxis1);
      weight = (rowEnd + 1 - rowStart);
      for (iRow=0; iRow < *pNaxis2; iRow++) {
         pOut[iRow] = 0.0;
         for (iCol=rowStart; iCol <= rowEnd; iCol++) {
            pOut[iRow] += pData[iRow*(*pNaxis1) + iCol];
         }
         pOut[iRow] /= weight;
      }
   }

}

/******************************************************************************/
/*
 * Average several rows (or columns) of a 2-dimensional array of floats
 * with their standard deviations.  For each combined set of points:
 *    obj_ave = SUM_i {obj_i / sig_i^2} / SUM_i {1 / sig_i^2}
 *    sig_ave = 1 / SUM_i {1 / sig_i^2}
 * If (*iq)==0 then average rows; if (*iq)==1 then average columns.
 * Note that *pNaxis1=number of columns and *pNaxis2=number of rows.
 * Memory is dynamically allocated for the output vector.
 */
void fits_ave_obj_and_sigma_rows_r4_
  (int   *  iq,
   DSIZE *  pRowStart,
   DSIZE *  pNumRowAve,
   DSIZE *  pNaxis1,
   DSIZE *  pNaxis2,
   float ** ppObjData,
   float ** ppSigData,
   float ** ppObjOut,
   float ** ppSigOut)
{
   DSIZE   iCol;
   DSIZE   iRow;
   DSIZE   rowStart;
   DSIZE   rowEnd;
   DSIZE   iloc;
   MEMSZ   memSize;
   float   weight;
   float   oneOverSumVar;
   float * pObjData = *ppObjData;
   float * pSigData = *ppSigData;
   float * pObjOut;
   float * pSigOut;

   if (*iq == 0) {
      memSize = sizeof(float) * (*pNaxis1);
      ccalloc_(&memSize, (void **)ppObjOut);
      ccalloc_(&memSize, (void **)ppSigOut);
      pObjOut = *ppObjOut;
      pSigOut = *ppSigOut;
      rowStart = max(0, (*pRowStart));
      rowEnd = min((*pRowStart) + (*pNumRowAve) - 1, (*pNaxis2) - 1);
      for (iCol=0; iCol < *pNaxis1; iCol++) {
         pObjOut[iCol] = 0.0;
         oneOverSumVar = 0.0;
         for (iRow=rowStart; iRow <= rowEnd; iRow++) {
            iloc = iRow*(*pNaxis1) + iCol;
            weight = 1.0 / (pSigData[iloc] * pSigData[iloc]);
            pObjOut[iCol] += pObjData[iloc] * weight;
            oneOverSumVar += weight;
         }
         pObjOut[iCol] /= oneOverSumVar;
         pSigOut[iCol] = 1.0 / sqrt(oneOverSumVar);
      }

   } else if (*iq == 1) {
      memSize = sizeof(float) * (*pNaxis2);
      ccalloc_(&memSize, (void **)ppObjOut);
      ccalloc_(&memSize, (void **)ppSigOut);
      pObjOut = *ppObjOut;
      pSigOut = *ppSigOut;
      rowStart = max(0, (*pRowStart));
      rowEnd = min((*pRowStart) + (*pNumRowAve) - 1, (*pNaxis1) - 1);
      for (iRow=0; iRow < *pNaxis2; iRow++) {
         pObjOut[iRow] = 0.0;
         oneOverSumVar = 0.0;
         for (iCol=rowStart; iCol <= rowEnd; iCol++) {
            iloc = iRow*(*pNaxis1) + iCol;
            weight = 1.0 / (pSigData[iloc] * pSigData[iloc]);
            pObjOut[iRow] += pObjData[iloc] * weight;
            oneOverSumVar += weight;
         }
         pObjOut[iRow] /= oneOverSumVar;
         pSigOut[iRow] = 1.0 / sqrt(oneOverSumVar);
      }
   }

}

/******************************************************************************/
/*
 * Swap bytes between big-endian and little-endian.
 */
void fits_byteswap
  (int      bitpix,
   DSIZE    nData,
   uchar *  pData)
{
   int      ibits;
   DSIZE    idata;

   ibits = abs(bitpix);
   if (ibits == 16) {
      for (idata=0; idata < nData; idata++) {
         fits_bswap2( &pData[2*idata  ], &pData[2*idata+1] );
      }
   } else if (ibits == 32) {
      for (idata=0; idata < nData; idata++) {
         fits_bswap2( &pData[4*idata  ], &pData[4*idata+3] );
         fits_bswap2( &pData[4*idata+1], &pData[4*idata+2] );
      }
   } else if (ibits == 64) {
      for (idata=0; idata < nData; idata++) {
         fits_bswap2( &pData[8*idata  ], &pData[8*idata+7] );
         fits_bswap2( &pData[8*idata+1], &pData[8*idata+6] );
         fits_bswap2( &pData[8*idata+2], &pData[8*idata+5] );
         fits_bswap2( &pData[8*idata+3], &pData[8*idata+4] );
      }
   }

}

void fits_bswap2
  (uchar *  pc1,
   uchar *  pc2)
{
   uchar    ct;
   ct = *pc1;
   *pc1 = *pc2;
   *pc2 = ct;
}
