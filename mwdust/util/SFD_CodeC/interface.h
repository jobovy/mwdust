 
#ifndef __INCinterface_h
#define __INCinterface_h
 
/*
 * Deal with Fortran-C calling conventions.  Most unix Fortran
 * compilers add an extra trailing _ to fortran names, and so the
 * default values of FORTRAN_PREPEND and FORTRAN_APPEND are '' and '_'.
 */

/* Deal with Fortran--C name differences; the default is to add an _ */
#if defined(__SUN)
#  define FORTRAN_APPEND __
#endif
#if defined(__LINUX)
#  define FORTRAN_APPEND __
#endif
#if !defined(FORTRAN_APPEND)
#  define FORTRAN_APPEND _
#endif

#define _CONCATENATE(P,F) P ## F
#define CONCATENATE(P,F) _CONCATENATE(P,F)

#if defined(FORTRAN_PREPEND)
#   if defined(FORTRAN_APPEND)
#      define DECLARE(F) \
                CONCATENATE(FORTRAN_PREPEND,CONCATENATE(F,FORTRAN_APPEND))
#   else
#      define DECLARE(F) CONCATENATE(FORTRAN_PREPEND,F)
#   endif
#else
#   if defined(FORTRAN_APPEND)
#      define DECLARE(F) CONCATENATE(F,FORTRAN_APPEND)
#   else
#      define DECLARE(F) F
#   endif
#endif

#endif /* __INCinterface_h */

