
#ifndef __INCsubs_fits_h
#define __INCsubs_fits_h

typedef unsigned char uchar;
typedef long int HSIZE;
typedef long int DSIZE;

void fits_read_file_fits_header_only_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead);
int fits_read_file_ascii_header_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead);
DSIZE fits_read_file_fits_r4_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   float ** ppData);
DSIZE fits_read_file_fits_i2_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   short int ** ppData);
DSIZE fits_read_subimg_
  (char     pFileName[],
   HSIZE    nHead,
   uchar *  pHead,
   DSIZE *  pStart,
   DSIZE *  pEnd,
   DSIZE *  pNVal,
   float ** ppVal);
void fits_read_subimg1
  (int      nel,
   DSIZE *  pNaxis,
   DSIZE *  pStart,
   DSIZE *  pEnd,
   int      fileNum,
   int      bitpix,
   DSIZE *  pNVal,
   uchar *  pData);
DSIZE fits_read_point_
  (char     pFileName[],
   HSIZE    nHead,
   uchar *  pHead,
   DSIZE *  pLoc,
   float *  pValue);
DSIZE fits_read_file_fits_noscale_
  (char     pFileName[],
   DSIZE *  pNHead,
   uchar ** ppHead,
   HSIZE *  pNData,
   int   *  pBitpix,
   uchar ** ppData);
DSIZE fits_read_file_xfits_noscale_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   HSIZE *  pNxhead,
   uchar ** ppXhead,
   DSIZE *  pNData,
   int   *  pBitpix,
   uchar ** data);
DSIZE fits_write_file_fits_r4_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   float ** ppData);
DSIZE fits_write_file_fits_i2_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   short int ** ppData);
DSIZE fits_write_file_fits_noscale_
  (char     pFileName[],
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   int   *  pBitpix,
   uchar ** ppData);
DSIZE fits_read_fits_data_
  (int   *  pFilenum,
   int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData);
DSIZE fits_write_fits_data_
  (int   *  pFilenum,
   int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData);
void fits_read_fits_header_
  (int   *  pFilenum,
   HSIZE *  pNHead,
   uchar ** ppHead);
void fits_skip_header_
  (int   *  pFilenum);
void fits_add_required_cards_
  (HSIZE *  pNHead,
   uchar ** ppHead);
void fits_write_fits_header_
  (int   *  pFilenum,
   HSIZE *  pNHead,
   uchar ** ppHead);
void fits_create_fits_header_
  (HSIZE *  pNHead,
   uchar ** ppHead);
void fits_duplicate_fits_header_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   uchar ** ppHeadCopy);
void fits_duplicate_fits_data_r4_
  (DSIZE *  pNData,
   float ** ppData,
   float ** ppDataCopy);
void fits_duplicate_fits_data_
  (int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData,
   uchar ** ppDataCopy);
void fits_create_fits_data_r4_
  (DSIZE *  pNData,
   float ** ppData);
void fits_create_fits_data_
  (int   *  pBitpix,
   DSIZE *  pNData,
   uchar ** ppData);
int fits_dispose_header_and_data_
  (uchar ** ppHead,
   uchar ** ppData);
int fits_dispose_array_
  (uchar ** ppHeadOrData);
DSIZE fits_compute_ndata_
  (HSIZE *  pNHead,
   uchar ** ppHead);
void fits_compute_axes_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   int   *  pNumAxes,
   DSIZE ** ppNaxis);
void fits_free_axes_
  (int   *  pNumAxes,
   DSIZE ** ppNaxis);
float compute_vista_wavelength_
  (DSIZE *  pPixelNumber,
   int   *  pNCoeff,
   float ** ppCoeff);
void fits_compute_vista_poly_coeffs_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   int   *  pNCoeff,
   float ** ppCoeff);
void fits_data_to_r4_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData);
void fits_data_to_i2_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData);
HSIZE fits_add_card_
  (uchar    pCard[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_add_cardblank_
  (uchar    pCard[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_add_card_ival_
  (int   *  pIval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_add_card_rval_
  (float *  pRval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_add_card_string_
  (char  *  pStringVal,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_add_card_comment_
  (char  *  pStringVal,
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_add_card_history_
  (char  *  pStringVal,
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_purge_blank_cards_
  (HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_delete_card_
  (uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_find_card_
  (uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
void fits_swap_cards_ival_
  (uchar *  pLabel1,
   uchar *  pLabel2,
   HSIZE *  pNHead,
   uchar ** ppHead);
void fits_swap_cards_rval_
  (uchar *  pLabel1,
   uchar *  pLabel2,
   HSIZE *  pNHead,
   uchar ** ppHead);
int fits_get_card_ival_
  (int   *  pIval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
int fits_get_card_rval_
  (float *  pRval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
int fits_get_card_date_
  (int   *  pMonth,
   int   *  pDate,
   int   *  pYear,
   uchar    pLabelDate[],
   HSIZE *  pNHead,
   uchar ** ppHead);
int fits_get_card_time_
  (float *  pTime,
   uchar    pLabelTime[],
   HSIZE *  pNHead,
   uchar ** ppHead);
int fits_get_card_string_
  (char  ** ppStringVal,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_change_card_
  (uchar    pCard[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_change_card_ival_
  (int   *  pIval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
HSIZE fits_change_card_rval_
  (float *  pRval,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHhead);
HSIZE fits_change_card_string_
  (char  *  pStringVal,
   uchar    pLabel[],
   HSIZE *  pNHead,
   uchar ** ppHead);
void fits_string_to_card_
  (uchar    pString[],
   uchar    pCard[]);
float fits_get_rval_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBscale,
   float *  pBzero,
   uchar ** ppDdata);
int fits_get_ival_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBscale,
   float *  pBzero,
   uchar ** ppDdata);
void fits_put_rval_
  (float *  pRval,
   DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBscale,
   float *  pBzero,
   uchar ** ppData);
int fits_qblankval_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBlankval,
   uchar ** ppDdata);
void fits_put_blankval_
  (DSIZE *  pIloc,
   int   *  pBitpix,
   float *  pBlankval,
   uchar ** ppData);
void fits_purge_nulls
  (uchar    pCard[]);
int fits_get_next_card_
  (int   *  pFilenum,
   uchar    pCard[]);
int fits_put_next_card_
  (int   *  pFilenum,
   uchar    pCard[]);
int fits_size_from_bitpix_
  (int   *  pBitpix);
void fits_pixshift_wrap_
  (int   *  pSAxis,
   DSIZE *  pShift,
   HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData);
void fits_transpose_data_
  (HSIZE *  pNHead,
   uchar ** ppHead,
   DSIZE *  pNData,
   uchar ** ppData);
void fits_ave_rows_r4_
  (int   *  iq,
   DSIZE *  pRowStart,
   DSIZE *  pNumRowAve,
   DSIZE *  pNaxis1,
   DSIZE *  pNaxis2,
   float ** ppData,
   float ** ppOut);
void fits_ave_obj_and_sigma_rows_r4_
  (int   *  iq,
   DSIZE *  pRowStart,
   DSIZE *  pNumRowAve,
   DSIZE *  pNaxis1,
   DSIZE *  pNaxis2,
   float ** ppObjData,
   float ** ppSigData,
   float ** ppObjOut,
   float ** ppSigOut);
void fits_byteswap
  (int      bitpix,
   DSIZE    nData,
   uchar *  pData);
void fits_bswap2
  (uchar *  pc1,
   uchar *  pc2);

extern uchar * datum_zero;
extern uchar * label_airmass;
extern uchar * label_bitpix;
extern uchar * label_blank;
extern uchar * label_bscale;
extern uchar * label_bzero;
extern uchar * label_ctype1;
extern uchar * label_ctype2;
extern uchar * label_cdelt1;
extern uchar * label_cdelt2;
extern uchar * label_cd1_1;
extern uchar * label_cd1_2;
extern uchar * label_cd2_1;
extern uchar * label_cd2_2;
extern uchar * label_latpole;
extern uchar * label_lonpole;
extern uchar * label_crpix1;
extern uchar * label_crpix2;
extern uchar * label_crval1;
extern uchar * label_crval2;
extern uchar * label_date_obs;
extern uchar * label_dec;
extern uchar * label_empty;
extern uchar * label_end;
extern uchar * label_exposure;
extern uchar * label_extend;
extern uchar * label_filtband;
extern uchar * label_filter;
extern uchar * label_ha;
extern uchar * label_instrume;
extern uchar * label_lamord;
extern uchar * label_loss;
extern uchar * label_naxis;
extern uchar * label_naxis1;
extern uchar * label_naxis2;
extern uchar * label_object;
extern uchar * label_observer;
extern uchar * label_pa;
extern uchar * label_platescl;
extern uchar * label_ra;
extern uchar * label_rnoise;
extern uchar * label_rota;
extern uchar * label_seeing;
extern uchar * label_skyrms;
extern uchar * label_skyval;
extern uchar * label_slitwidt;
extern uchar * label_st;
extern uchar * label_telescop;
extern uchar * label_time;
extern uchar * label_tub;
extern uchar * label_ut;
extern uchar * label_vhelio;
extern uchar * label_vminusi;
extern uchar * card_simple;
extern uchar * card_empty;
extern uchar * card_null;
extern uchar * card_end;
extern uchar * text_T;
extern uchar * text_F;

#endif /* __INCsubs_fits_h */
