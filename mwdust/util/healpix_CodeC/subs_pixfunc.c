// This code was ported and modified to C from Koike Michitaro's TypeScript implementation of Healpix under the MIT License
// Original Copyright 2018 Michitaro Koike
// this code is good up to 29th zoom level up from 16th zoom level from the original TypeScript implementation
// Reference papaer: http://iopscience.iop.org/article/10.1086/427976/pdf

#include <math.h>
#include <assert.h>
#include <stdlib.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#elif defined __GNUC__
#define EXPORT __attribute__((visibility("default")))
#else
#define EXPORT
#endif

#ifdef _WIN32
#include <Python.h>
PyMODINIT_FUNC PyInit_healpix_c(void)
{ // Python 3
    return NULL;
};
#endif

// theta range is colatitude in radians measured southward from north pole in (0, pi)
// phi range is longitude in radians, measured eastward in (0, 2pi)

// Position for poles
double sigma(double z)
{
    if (z < 0)
    {
        return -sigma(-z);
    }
    else
    {
        return 2 - sqrt(3 * (1 - z));
    }
}

// double distance2(double *a, double *b) {
//     return sqrt(pow(a[0] - b[0], 2) + pow(a[1] - b[1], 2) + pow(a[2] - b[2], 2) * 1.0);

// }

// double angle(double *a, double *b) {
//     return 2 * asin(sqrt(distance2(a, b)) / 2);
// }

double sign(double x)
{
    return (x > 0) - (x < 0);
}

// HEALPix spherical projection
void za2tu(double z, double a, double *t, double *u)
{
    if (fabs(z) <= 2. / 3.)
    // equator
    {
        *t = a;
        *u = 3 * (M_PI / 8.) * z;
    }
    else
    // north/south poles
    {
        double sigma_z;
        sigma_z = sigma(z);
        *t = a - (fabs(sigma_z) - 1) * (fmod(a, M_PI / 2.) - (M_PI / 4.));
        *u = (M_PI / 4.) * sigma_z;
    }
}

// RING to NEST order
void bit_combine(long long int x, long long int y, long long int *p)
{
    assert(x < (1 << 29));
    assert(y < (1 << 28));
    *p = (x & 1 | (x & 0x2LL | y & 0x1LL) << 1 | (x & 0x4LL | y & 0x2LL) << 2 | (x & 0x8LL | y & 0x4LL) << 3 | (x & 0x10LL | y & 0x8LL) << 4 | (x & 0x20LL | y & 0x10LL) << 5 | (x & 0x40LL | y & 0x20LL) << 6 | (x & 0x80LL | y & 0x40LL) << 7 | (x & 0x100LL | y & 0x80LL) << 8 | (x & 0x200LL | y & 0x100LL) << 9 | (x & 0x400LL | y & 0x200LL) << 10 | (x & 0x800LL | y & 0x400LL) << 11 | (x & 0x1000LL | y & 0x800LL) << 12 | (x & 0x2000LL | y & 0x1000LL) << 13 | (x & 0x4000LL | y & 0x2000LL) << 14 | (x & 0x8000LL | y & 0x4000LL) << 15 | (x & 0x10000LL | y & 0x8000LL) << 16 | (x & 0x20000LL | y & 0x10000LL) << 17 | (x & 0x40000LL | y & 0x20000LL) << 18 | (x & 0x80000LL | y & 0x40000LL) << 19 | (x & 0x100000LL | y & 0x80000LL) << 20 | (x & 0x200000LL | y & 0x100000LL) << 21 | (x & 0x400000LL | y & 0x200000LL) << 22 | (x & 0x800000LL | y & 0x400000LL) << 23 | (x & 0x1000000LL | y & 0x800000LL) << 24 | (x & 0x2000000LL | y & 0x1000000LL) << 25 | (x & 0x4000000LL | y & 0x2000000LL) << 26 | (x & 0x8000000LL | y & 0x4000000LL) << 27 | (x & 0x10000000LL | y & 0x8000000LL) << 28 | (x & 0x20000000LL | y & 0x10000000LL) << 29 | y & 0x20000000LL << 30);
}

void bit_decombine(long long int p, long long int *x, long long int *y)
{
    assert(p <= 0x7fffffffLL);
    *x = (p & 0x1LL) >> 0 | (p & 0x4LL) >> 1 | (p & 0x10LL) >> 2 | (p & 0x40LL) >> 3 | (p & 0x100LL) >> 4 | (p & 0x400LL) >> 5 | (p & 0x1000LL) >> 6 | (p & 0x4000LL) >> 7 | (p & 0x10000LL) >> 8 | (p & 0x40000LL) >> 9 | (p & 0x100000LL) >> 10 | (p & 0x400000LL) >> 11 | (p & 0x1000000LL) >> 12 | (p & 0x4000000LL) >> 13 | (p & 0x10000000LL) >> 14 | (p & 0x40000000LL) >> 15 | (p & 0x100000000LL) >> 16 | (p & 0x400000000LL) >> 17 | (p & 0x1000000000LL) >> 18 | (p & 0x4000000000LL) >> 19 | (p & 0x10000000000LL) >> 20 | (p & 0x40000000000LL) >> 21 | (p & 0x100000000000LL) >> 22 | (p & 0x400000000000LL) >> 23 | (p & 0x1000000000000LL) >> 24 | (p & 0x4000000000000LL) >> 25 | (p & 0x10000000000000LL) >> 26 | (p & 0x40000000000000LL) >> 27 | (p & 0x100000000000000LL) >> 28;
    *y = (p & 0x2LL) >> 1 | (p & 0x8LL) >> 2 | (p & 0x20LL) >> 3 | (p & 0x80LL) >> 4 | (p & 0x200LL) >> 5 | (p & 0x800LL) >> 6 | (p & 0x2000LL) >> 7 | (p & 0x8000LL) >> 8 | (p & 0x20000LL) >> 9 | (p & 0x80000LL) >> 10 | (p & 0x200000LL) >> 11 | (p & 0x800000LL) >> 12 | (p & 0x2000000LL) >> 13 | (p & 0x8000000LL) >> 14 | (p & 0x20000000LL) >> 15 | (p & 0x80000000LL) >> 16 | (p & 0x200000000LL) >> 17 | (p & 0x800000000LL) >> 18 | (p & 0x2000000000LL) >> 19 | (p & 0x8000000000LL) >> 20 | (p & 0x20000000000LL) >> 21 | (p & 0x80000000000LL) >> 22 | (p & 0x200000000000LL) >> 23 | (p & 0x800000000000LL) >> 24 | (p & 0x2000000000000LL) >> 25 | (p & 0x8000000000000LL) >> 26 | (p & 0x20000000000000LL) >> 27 | (p & 0x80000000000000LL) >> 28;
}

double wrap(double A, double B)
{
    if (A < 0)
    {
        return B - fmod(-A, B);
    }
    else
    {
        return fmod(A, B);
    }
}

double clip(double Z, double A, double B)
{
    if (Z < A)
    {
        return A;
    }
    else if (Z > B)
    {
        return B;
    }
    else
    {
        return Z;
    }
}

// spherical projection to base pixel index
// f: base pixel index
// p: coord in north east axis of base pixel
// q: coord in north west axis of base pixel
void tu2fpq(double t, double u, long long int *f, double *p, double *q)
{
    double pp;
    int PP;
    double qq;
    int QQ;
    int V;
    t /= (M_PI / 4.);
    u /= (M_PI / 4.);
    t = wrap(t, 8.);
    t += -4.;
    u += 5.;
    pp = clip((u + t) / 2., 0., 5.);
    PP = floor(pp);
    qq = clip((u - t) / 2., 3. - PP, 6. - PP);
    QQ = floor(qq);
    V = 5 - (PP + QQ);
    if (V < 0)
    { // clip
        *f = 0;
        *p = 1.;
        *q = 1.;
    }
    else
    {
        *f = 4 * V + fmod(((PP - QQ + 4) >> 1), 4.);
        *p = fmod(pp, 1);
        *q = fmod(qq, 1);
    }
}

void fxy2tu(int nside, long long int f, long long int x, long long int y, double *t, double *u)
{
    double f_row;
    double i;
    double k;
    f_row = floor(f / 4);
    i = (f_row + 2) * nside - (x + y) - 1.;
    k = ((2 * (fmod(f, 4)) - (fmod(f_row, 2)) + 1) * nside + (x - y) + (8 * nside));
    *t = k / nside * (M_PI / 4.);
    *u = (M_PI / 2.) - i / nside * (M_PI / 4.);
}

void tu2za(double t, double u, double *z, double *a)
{
    double abs_u;
    abs_u = fabs(u);
    double t_t;
    if (abs_u >= M_PI / 2.)
    { // error
        *z = sign(u);
        *a = 0;
    }
    if (abs_u <= M_PI / 4.)
    { // equatorial belt
        *z = 8. / (3. * M_PI) * u;
        *a = t;
    }
    else
    { // polar caps
        *a = t - (abs_u - (M_PI / 4.)) / (abs_u - (M_PI / 2.)) * (fmod(t, (M_PI / 2.)) - (M_PI / 4.));
        *z = sign(u) * (1. - (1. / 3.) * pow((2 - 4 * abs_u / M_PI), 2.));
    }
}

void tu2fxy(int nside, double t, double u, long long int *f, long long int *x, long long int *y)
{
    double p;
    double q;
    tu2fpq(t, u, f, &p, &q);
    *x = clip(floor(nside * p), 0, nside - 1);
    *y = clip(floor(nside * q), 0, nside - 1);
}

long long int fxy2nest(int nside, long long int f, int x, int y)
{
    long long int p;
    bit_combine(x, y, &p);
    return f * nside * nside + p;
}

long long int za2pix_nest(int nside, double z, double a)
{
    double t;
    double u;
    long long int f;
    long long int x;
    long long int y;
    za2tu(z, a, &t, &u);
    tu2fxy(nside, t, u, &f, &x, &y);
    return fxy2nest(nside, f, x, y);
}

void za2vec(double z, double a, double *xyz)
{
    double sin_theta;
    double x;
    double y;
    sin_theta = sqrt(1 - z * z);
    x = sin_theta * cos(a);
    y = sin_theta * sin(a);
    *xyz++ = x;
    *xyz++ = y;
    *xyz++ = z;
}

void za2ang(double z, double a, double *ang)
{
    double x;
    x = acos(z);
    *ang++ = x;
    *ang++ = fmod(a, 2. * M_PI);
}

void tu2vec(double t, double u, double *xyz)
{
    double z;
    double a;
    tu2za(t, u, &z, &a);
    za2vec(z, a, xyz);
}

// only single NEST pixel to single za
void nest2fxy(int nside, long long int ipix, long long int *f, long long int *x, long long int *y)
{
    int nside2;
    long long int k;
    nside2 = nside * nside;
    *f = floor(ipix / nside2);
    k = ipix % nside2;
    bit_decombine(k, x, y);
}

// only single pixel to single za
void pix2za_nest(int nside, int ipix, double *z, double *a)
{
    long long int f;
    long long int x;
    long long int y;
    double t;
    double u;
    nest2fxy(nside, ipix, &f, &x, &y);
    fxy2tu(nside, f, x, y, &t, &u);
    tu2za(t, u, z, a);
}

EXPORT long long int *ang2pix_nest(int nside, double *theta, double *phi, int nstars)
{
    long long int *tpix = (long long int *)malloc((size_t)(sizeof(long long int) * nstars));
    int istar;
    double z;
    for (istar = 0; istar < nstars; istar++)
    {
        // normalize coords
        z = cos(theta[istar]);
        tpix[istar] = za2pix_nest(nside, z, phi[istar]);
    }
    return tpix;
}

EXPORT double *ang2vec(double *theta, double *phi, int nstars)
{
    double *xyz_vec = (double *)malloc((size_t)(sizeof(double) * nstars * 3));
    int istar;
    double z;
    for (istar = 0; istar < nstars; istar++)
    {
        z = cos(theta[istar]);
        za2vec(z, phi[istar], xyz_vec + (3 * istar));
    }
    return xyz_vec;
}

EXPORT double *pix2vec_nest(int nside, int npix, long long int *ipix)
{
    double z;
    double a;
    int istar;
    double *xyz = (double *)malloc((size_t)(sizeof(double) * npix * 3));
    for (istar = 0; istar < npix; istar++)
    {
        pix2za_nest(nside, ipix[istar], &z, &a);
        za2vec(z, a, xyz + (3 * istar));
    }
    return xyz;
}

EXPORT double *pix2ang_nest(int nside, int npix, long long int *ipix)
{
    double z;
    double a;
    int istar;
    double *ang = (double *)malloc((size_t)(sizeof(double) * npix * 2));
    for (istar = 0; istar < npix; istar++)
    {
        pix2za_nest(nside, ipix[istar], &z, &a);
        za2ang(z, a, ang + (2 * istar));
    }
    return ang;
}
