# Test that asking for E(B-V) returns the correct value for all dust maps
import numpy
import mwdust

def test_SFD():
    sfd_ebv= mwdust.SFD(filter='E(B-V)')
    sfd_b= mwdust.SFD(filter='Landolt B')
    sfd_v= mwdust.SFD(filter='Landolt V')
    l,b,d= 10., 1., 2.
    assert numpy.fabs(sfd_ebv(l,b,d)-(sfd_b(l,b,d)-sfd_v(l,b,d))) \
         < 10.**-12., \
        'SFD E(B-V) does not agree with A(B)-A(V)'
    return None

def test_Drimmel03():
    drim_ebv= mwdust.Drimmel03(filter='E(B-V)')
    drim_b= mwdust.Drimmel03(filter='Landolt B')
    drim_v= mwdust.Drimmel03(filter='Landolt V')
    l,b,d= 10., 1., 2.
    assert numpy.fabs(drim_ebv(l,b,d)-(drim_b(l,b,d)-drim_v(l,b,d))) \
         < 10.**-12., \
        'Drimmel03 E(B-V) does not agree with A(B)-A(V)'
    return None

def test_Marshall06():
    mar_ebv= mwdust.Marshall06(filter='E(B-V)')
    mar_b= mwdust.Marshall06(filter='Landolt B')
    mar_v= mwdust.Marshall06(filter='Landolt V')
    l,b,d= 10., 1., 2.
    assert numpy.fabs(mar_ebv(l,b,d)-(mar_b(l,b,d)-mar_v(l,b,d))) \
         < 10.**-12., \
        'Marshall06 E(B-V) does not agree with A(B)-A(V)'
    return None

def test_Green19():
    # Need to preserve memory
    l,b,d= 10., 1., 2.
    green_ebv= mwdust.Green19(filter='E(B-V)')
    ebv= green_ebv(l,b,d)
    del green_ebv
    green_b= mwdust.Green19(filter='Landolt B')
    ab= green_b(l,b,d)
    del green_b
    green_v= mwdust.Green19(filter='Landolt V')
    av= green_v(l,b,d)
    assert numpy.fabs(ebv-(ab-av)) \
         < 10.**-12., \
        'Green19 E(B-V) does not agree with A(B)-A(V)'
    return None

def test_Combined15():
    # Need to preserve memory
    l,b,d= 10., 1., 2.
    combined_ebv= mwdust.Combined15(filter='E(B-V)')
    ebv= combined_ebv(l,b,d)
    del combined_ebv
    combined_b= mwdust.Combined15(filter='Landolt B')
    ab= combined_b(l,b,d)
    del combined_b
    combined_v= mwdust.Combined15(filter='Landolt V')
    av= combined_v(l,b,d)
    assert numpy.fabs(ebv-(ab-av)) \
         < 10.**-12., \
        'Combined15 E(B-V) does not agree with A(B)-A(V)'
    return None
