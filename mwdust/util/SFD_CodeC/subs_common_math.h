
#ifndef __INCsubs_common_math_h
#define __INCsubs_common_math_h

#define min(a,b) ( ((a) < (b)) ? (a) : (b) )
#define max(a,b) ( ((a) > (b)) ? (a) : (b) )
#define SIGN(a)  ( ((a) >= 0.0) ? (1.0) : (-1.0) )
#define TRUE  1
#define FALSE 0

#if 0
static float minarg1,minarg2;
#define FMIN(a,b) (minarg1=(a),minarg2=(b),(minarg1) < (minarg2) ?\
        (minarg1) : (minarg2))
static float maxarg1,maxarg2;
#define FMAX(a,b) (maxarg1=(a),maxarg2=(b),(maxarg1) > (maxarg2) ?\
        (maxarg1) : (maxarg2))
#endif

float FMIN
  (float    a,
   float    b);
float FMAX
  (float    a,
   float    b);
void vector_copy
  (int      nData,
   float *  pDataIn,
   float *  pDataOut);
float vector_minimum
  (int      nData,
   float *  pData);
float vector_maximum
  (int      nData,
   float *  pData);
float vector_mean
  (int      nData,
   float *  pData);
int ivector_sum
  (int      nData,
   int   *  pData);
float vector_sum
  (int      nData,
   float *  pData);
float vector_dispersion_about_zero
  (int      nData,
   float *  pData);
void vector_mean_and_dispersion
  (int      nData,
   float *  pData,
   float *  pMean,
   float *  pDispersion);
void vector_mean_and_dispersion_with_errs
  (int      nData,
   float *  pData,
   float *  pErr,
   float *  pMean,
   float *  pDispersion);
void vector_moments
  (int      nData,
   float *  pData,
   float *  pMean,
   float *  pVar,
   float *  pSkew,
   float *  pKurt);
int vector_closest_value
  (float    x,
   int      nData,
   float *  pData);
int vector_furthest_value
  (float    x,
   int      nData,
   float *  pData);
int vector_lower_value
  (float    x,
   int      nData,
   float *  pData);
int vector_higher_value
  (float    x,
   int      nData,
   float *  pData);
float vector_interpolated_index
  (float    x,
   int      nData,
   float *  pData);
float quadrature_sum
  (float    term1,
   float    term2);
void subtract_med_filter_vector
  (int      filtSize,
   int      nData,
   float *  pData);
void boxcar_filter_vector
  (int      filtSize,
   int      nData,
   float *  pData);
void median_filter_vector
  (int      filtSize,
   int      nData,
   float *  pData);
float vector_median
  (int      nData,
   float *  pData);
float vector_selip
  (int      kData,
   int      nData,
   float *  pData);
void ivector_sort_and_unique
  (int   *  pNData,
   int   ** ppData);
int vector_subtract_poly_fit_with_rej
  (int      nData,
   float *  pDataX,
   float *  pDataY,
   float    sigRejLo,
   float    sigRejHi,
   int      growRej,
   int      nRejIter,
   int      nCoeff);
int vector_poly_fit_with_rej
  (int      nData,
   float *  pDataX,
   float *  pDataY,
   float    sigRejLo,
   float    sigRejHi,
   int      growRej,
   int      nRejIter,
   int      nCoeff,
   float *  pCoeff,
   float *  pChi2);
float vector_percentile_value_with_rej
  (int      nData,
   float *  pDataVal,
   float *  pDataErr,
   float    fSelip,
   float    sigRejLo,
   float    sigRejHi,
   int      nRejIter);
void sort_structure_on_float
  (int      nData,
   int      structLen,
   float *  pFloatAddress,
   unsigned char *  pStructAddress);
int fit_exponential
  (int      nData,
   float *  pXaxis,
   float *  pYaxis,
   float *  pSigma,
   int      nCCoeff,
   float *  pCCoeff,
   int   *  pDOF,
   float *  pChi2);
void func_wderiv_exponential
  (float    x,
   float    a[],
   float *  y,
   float    dyda[],
   int      na);
 
#endif /* __INCsubs_common_math_h */
