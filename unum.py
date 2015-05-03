from __future__ import division

import math
open = True
closed = False
print open
from fractions import *
e = 3
f = 4
esizesize = e
fsizesize = f
esizemax = 2**esizesize
fsizemax = 2**fsizesize
utagsize = 1 + f + e
maxubits = 1 + esizemax + fsizemax + utagsize
ubitmask = 1 << (utagsize - 1)
fsizemask = (1 << f) - 1
esizemask = (ubitmask - 1) - fsizemask
efsizemask = esizemask | fsizemask
utagmask = ubitmask | efsizemask
ulpu = 1 << utagsize
smallsubnormalu = efsizemask + ulpu
smallnormalu = efsizemask + (1 << (maxubits - 1 - esizemax))
signbigu = 1 << maxubits - 1
posinfu = signbigu - 1 - ubitmask
maxrealu = posinfu - ulpu
minrealu = maxrealu + signbigu
neginfu = posinfu + signbigu
qNaNu = posinfu + ubitmask
sNaNu = neginfu + ubitmask
NaN = float("nan")

maxreal = 2**(2**(esizemax-1)) * (2**fsizemax - 1) / (2**fsizemax)
smallsubnormal = 2**(2 - 2**(esizemax-1) - fsizemax)

def fractionalPart(x):
    return x - (x // 1)

def integerPart(x):
    return x // 1

def log(x, base):
    return math.log(x, base)

def floor(x):
    return int(math.floor(x))

def unumQ(x):
    if isinstance(x, int):
        if x >= 0 and x <= sNaNu:
            return True
    return False

def uQ(x):
    return unumQ(x) or uboundQ(x)

def unum2g(u):
    if unumQ(u):
        if u == qNaNu or u == sNaNu:
            return ((NaN, NaN), (open, open))
        x = u2f(exact(u))
        y = u2f(exact(u) + ulpu)
        if exQ(u):
            return ((x, x), (closed, closed))
        elif u == (bigu(u) + ubitmask):
            return ((big(u), float('inf')), (open, open))
        elif u == signmask(u) + bigu(u) + ubitmask:
            return ((float('-inf'), -big(u)), (open, open))
        elif sign(u) == 1:
            return ((y, x), (open, open))
        else:
            return ((x, y), (open, open))

def floatQ(x):
    return True

def exQ(x):
    return True

def esizeminus1(u):
    if unumQ(u):
        return (u & esizemask) >> fsizesize

def esize(u):
    if unumQ(u):
        return 1 + esizeminus1(u)

def fsizeminus1(u):
    if unumQ(u):
        return u & fsizemask

def fsize(u):
    if unumQ(u):
        return 1 + fsizeminus1(u)

def numbits(u):
    if unumQ(u):
        return 1 + esize(u) + fsize(u) + utagsize

def signmask(u):
    if unumQ(u):
        return 1 << (numbits(u) - 1)

def hiddenmask(u):
    if unumQ(u):
        return 1 << (fsize(u) + utagsize)
def fracmask(u):
    if unumQ(u):
        return ((1 << fsize(u)) - 1) << utagsize

def expomask(u):
    if unumQ(u):
        return ((1 << esize(u)) - 1) << (fsize(u) + utagsize)
def floatmask(u):
    if unumQ(u):
        return signmask(u) + expomask(u) + fracmask(u)

def bias(u):
    if unumQ(u):
        return 2**(esizeminus1(u)) - 1
def sign(u):
    if unumQ(u):
        return (u & signmask(u) > 0)
def expo(u):
    if unumQ(u):
        return (u & expomask(u)) >> (utagsize + fsize(u))
def hidden(u):
    if unumQ(u):
        return expo(u) > 0
def frac(u):
    if unumQ(u):
        return (u & fracmask(u)) >> utagsize

def inexQ(u):
    if unumQ(u):
        return (u & ubitmask) > 0

def exQ(u):
    if unumQ(u):
        return (u & ubitmask) == 0

def exact(u):
    if unumQ(u):
        if inexQ(u):
            return u ^ ubitmask
        else:
            return u

def expovalue(u):
    if unumQ(u):
        return expo(u) - bias(u) + 1 - hidden(u)

def u2f(u):
    if unumQ(u) and exQ(u):
        if u == posinfu:
            return float("inf")
        if u == neginfu:
            return -float("inf")
        return ((-1)**sign(u))*(2**expovalue(u))*(hidden(u) + Fraction(frac(u), 2**fsize(u)))

def bigu(u):
    if unumQ(u):
        return expomask(u) + fracmask(u) + (efsizemask & u) - ulpu * ((u & efsizemask) == efsizemask)

def gQ(x):
    if isinstance(x, tuple):
        if len(x) == 2:
            if isinstance(x[0], tuple):
                if len(x[0]) == 2:
                    if isinstance(x[1], tuple):
                        if len(x[1]) == 2:
                            if isinstance(x[1][0], bool) and isinstance(x[1][1], bool) and floatQ(x[0][0]) and floatQ(x[0][1]):
                                if math.isnan(x[1][1]) or math.isnan(x[0][1]):
                                    return True
                                if (x[0][0] == x[0][1] and not x[1][0] and not x[1][1]) or x[0][0] < x[0][1]:
                                    return True
    return False

def uboundQ(x):
    if isinstance(x, tuple):
        if len(x) == 1 or len(x) == 2:
            xL = x[0]
            xR = x[-1]
            if unumQ(xL) and unumQ(xR):
                gL, gR = (unum2g(xL), unum2g(xR))
                if len(x) == 1 or (xL == qNaNu or xL == sNaNu or xR == qNaNu or xR == sNaNu) or \
                        ((gL[0][0] < gR[0][1]) or (gL[0][0] == gR[0][1] and (exQ(xL) and exQ(xR)))):
                            return True
    return False

# should this look at negative inf?
def scale(x):
    if floatQ(x) and x != float("inf") and not math.isnan(x):
        if x == 0:
            return 0
        else:
            return floor(log(abs(x),2))

def ne(x):
    if floatQ(x) and x != float("inf") and not math.isnan(x):
        if x == 0 and scale(x) == 1:
            return 1
        else:
            return int(math.ceil(log(1+abs(scale(x)-1),2))) + 1

def nbits(u):
    if uQ(u):
        if unumQ(u):
            ub = (u,)
        else:
            ub = u
        if len(ub) == 2:
            return 1 + numbits(ub[0]) + numbits(ub[1])
        else:
            return 1 + numbits(ub[0])

def ubound2g(ub):
    if uboundQ(ub):
        uL = ub[0]
        uR = ub[-1]
        if uL == qNaNu or uL == sNaNu or uR == qNaNu or uR == sNaNu:
            return ((float("nan"), float("nan")), (open, open))
        gL, gR = (unum2g(uL), unum2g(uR))
        return ((gL[0][0], gR[0][1]), (gL[1][0], gR[1][1]))

def u2g(u):
    if uQ(u):
        if unumQ(u):
            return unum2g(u)
        else:
            return ubound2g(u)

def x2u(x):
    if floatQ(x):
        if math.isnan(x):
            return qNaNu
        elif x == float("inf"):
            return posinfu
        elif x == float("-inf"):
            return neginfu
        elif abs(x) > maxreal:
            return maxrealu + ubitbask + (signbigu if x < 0 else 0)
        elif x == 0:
            return 0
        elif abs(x) < smallsubnormal:
            return utagmask + (signbigu if x < 0 else 0)
        elif abs(x) < u2f(smallnormalu):
            y = abs(x) / smallsubnormal
            y = (signbigu if x < 0 else 0) + efsizemask + (ubitmask if y != math.floor(y) else 0) + (math.floor(y), utagsize)
            # XXX is this right?
            assert(False)
            while ((3 << (utagsize - 1)) & y) == 0:
                y = (y - (efsizemask & y))/2 + (efsizemask & y) - 1
        else:
            n = 0
            y = abs(x) / 2**(scale(x))
            n = 0
            while math.floor(y) != y and n < fsizemax:
                n += 1
                y *= 2
            if y == math.floor(y): # the value is representable
                # exactly. Fill in the fields from right to left:
                # Size of fraction field,
                # fits in the rightmost fsizesize bits...
                y1 = n - (n > 0)
                # Size of exponent field minus 1 fits in the esizesize bits...
                y1 += ((ne(x) - 1) << fsizesize)
                # Significant bits after hidden bit fits left of the unum tag bits...
                y1 += 0 if n == 0 else ((floor(y) - 2**scale(y)) << utagsize)
                # Value of exponent bits, adjusted for bias...
                y1 += (scale(x) + 2**(ne(x) - 1) - 1) << (utagsize + n + (n == 0))
                # If negative, add the sign bit
                y1 += (1 << (utagsize + n + (n == 0) + ne(x))) if x < 0 else 0
                
                # if a number is more concise as a subnormal, make it one
                z = None
                try:
                    z = log(1 - log(abs(x), 2), 2)
                except:
                    pass
                if z and z.is_integer() and z >= 0:
                    return (z << fsizesize) + ulpu + (x < 0) * signmask(z << fsizesize)
                else:
                    return y1
            else:
                # inexact. Use all available fraction bits
                z = math.ceil(abs(x) / 2**(scale(x) - fsizemax)) * 2 ** (scale(x)-fsizemax)
                n = max(ne(x), ne(z))
                # All bits on for the fraction size, since we're using the maximum
                y1 = fsizemask
                # Store the exponent size minus 1 in the exponent size field
                y1 += (n - 1) << fsizesize
                # Back off by one ULP and make it inexact
                y1 += ubitmask - ulpu
                # Fraction bits are the ones to the left of the
                # binary point after removing hidden bit and scaling
                y1 += floor((z / 2**scale(z) - 1) * 2**fsizemax) << utagsize
                # Exponent value goes in the exponent field
                y1 += (scale(z) + 2**(n-1) - 1) << (utagsize + fsizemax)

                if x < 0:
                    y1 += signmask(y)
                return y1

def plusg(x, y):
    ((xlo, xhi), (xlob, xhib)) = x
    ((ylo, yhi), (ylob, yhib)) = y
    if math.isnan(xlo) or math.isnan(xhi) or math.isnan(ylo) or math.isnan(yhi):
        return ((NaN, open), (NaN,open))
    if xlo == float('-inf') and not xlob:
        (sumleft, openleft) = (NaN, open) if ylo == float("inf") and not ylob else (float("-inf"), closed)
    elif ylo == float('-inf') and not ylob:
        (sumleft, openleft) = (NaN, open) if xlo == float("inf") and not xlob else (float("-inf"), closed)
    elif (xlo == float('inf') and not xlob) or (ylo == float('inf') and not ylob):
        (sumleft, openleft) = (float('inf'), closed)
    elif xlo == float('-inf'):
        (sumleft, openleft) = (float('inf'), closed) if ylo == float('inf') and not ylob else (float('-inf'), open)
    elif ylo == float('-inf'):
        (sumleft, openleft) = (float('inf'), closed) if xlo == float('inf') and not xlob else (float('-inf'), open)
    else:
        (sumleft, openleft) = ((xlo + ylo), (xlob or ylob))
   
    if xhi == float('-inf') and not xhib:
        (sumright, openright) = (NaN, open) if yhi == float("inf") and not yhib else (float("-inf"), closed)
    elif yhi == float('-inf') and not yhib:
        (sumright, openright) = (NaN, open) if xhi == float("inf") and not xhib else (float("-inf"), closed)
    elif (xhi == float('inf') and not xhib) or (yhi == float('inf') and not yhib):
        (sumright, openright) = (float('inf'), closed)
    elif xhi == float('-inf'):
        (sumright, openright) = (float('inf'), closed) if yhi == float('inf') and not yhib else (float('-inf'), open)
    elif yhi == float('-inf'):
        (sumright, openright) = (float('inf'), closed) if xhi == float('inf') and not xhib else (float('-inf'), open)
    else:
        (sumright, openright) = ((xhi + yhi), (xhib or yhib))
    return ((sumleft, sumright), (openleft, openright))

def plusu(u, v):
    if uQ(u) and uQ(v):
        w = g2u(plusg(u2g(u), u2g(v)))
        global ubitsmoved, numbersmoved
        ubitsmoved += nbits(u) + nbits(v) + nbits(w)
        numbersmoved += 3
        return w

def negateg(x):
    return ((-x[0][0], -x[0][1]), (x[1][0], x[1][1]))

def minusg(x, y):
    return plusg(x, negateg(y))

def minusu(u, v):
    w = g2u(minusg(u2g(u), u2g(v)))
    global ubitsmoved, numbersmoved
    ubitsmoved += nbits(u) + nbits(v) + nbits(w)
    numbersmoved += 3
    return w

def ubright(xright):
    open = xright[1]
    u = x2u(xright[0])
    x = xright[0]
    if x == float('inf'):
        if open:
            return posopeninfu
        else:
            return posinfu
    if x == 0 and open:
        return negopenzerou
    if u2f(u) == x:
        if open:
            return (u - (ulpu * (x >= 0))) | ubitmask
        else:
            return u
    else:
        return u | (open * ubitmask)

def ubleft(xleft):
    open = xleft[1]
    u = x2u(xleft[0])
    x = xleft[0]
    if x == float('-inf'):
        if open:
            return negopeninfu
        else:
            return neginfu
    if x == 0 and open:
        return negopenzerou
    if u2f(u) == x:
        if open:
            return (u - (ulpu * (x < 0))) | ubitmask
        else:
            return u
    else:
        return u | (open * ubitmask)

def unifypos(ub):
    if uboundQ(ub):
        u = ub[0]
        v = ub[-1]
        # First do trivial case where endpoints express the same value
        if u2g(u) == u2g(v):
            return g2u(u2g(u))
        # Cannot unify if the interval includes exact 0, 1, 2, or 3
        if nnequQ(ub, x2u(0)) or nnequQ(ub, x2u(1)) or nnequQ(ub, x2u(2)) or nnequQ(ub, x2u(3)):
            return ub
        # Refine the endpoints for the tightest possible unification.
        u = promote(x2u(u2g(u)[0][0]), efsizemask)[0] + (ubitmask if inexQ(u) else -ubitmask)
        v = promote(x2u(u2g(v)[0][1]), efsizemask)[0] - (ubitmask if inexQ(v) else -ubitmask)
        if u == v:
            return (u,)
        # If upper bound is open inf and lower bound > maxreal, special handling is needed
        if u2g(v)[0][1] == float("inf") and u2g(v)[1][1]:
            if ltuQ((maxrealu,), (u,)):
                return (maxrealu + ubitmask,)
            # Defmote the left bound until the upper bound is open inf
            while u2g(u)[0][1] < float('inf'):
                if esize(u):
                    u = demotee(u)
                else:
                    u = demotef(u)
            return (u,)
        # While demoting exponents is possible and still leaves unums within ubound, demote both exponents
        while u != v and (((u2g(demotee(u))[0][0] < u2g(demotee(v))[0][0] and \
            u2g(demotee(u))[0][1] < u2g(demotee(v))[0][1]  < float('inf')))) and esize(u) > 1:
            u = demotee(u)
            v = demotee(v)
        while u != v and frac(v) != frac(u) and fsize(u) > 1:
            u = demotef(u)
            v = demotef(v)
        if u != v and ((floatmask(u) + ubitmask) | u) == ubitmask and ltuQ((v,), (x2u(1),)):
            n = min(esizemax, floor(log(1 - log(u2g(v + ubitmask if exQ[v] else 0)[0,1], 2), 2)))
            return (x2u(2**(-2**n+1)) - ubitmask,)
        else:
            if u == v:
                return (u,)
            else:
                return ub

def unify(ub):
    if uboundQ(ub):
        u = ub[0]
        v = ub[-1]
        if u == qNaNu or u == sNaNu or v == qNaNu or v == sNaNu:
            return (qNaNu,)
        if u == posinfu and v == posinfu:
            return (posinfu,)
        if u == neginfu and v == neginfu:
            return (neginfu,)
        if u == neginfu or u == posinfu or v == neginfu or v == posinfu or \
                ltuQ((u,), (x2u(0),)) and not ltuQ((v,), (x2u(0),)):
                    return (ub,)
        if ltuQ((u,), (x2u(0),)) and ltuQ((v,), (x2u(0),)):
            return negateu(unifypos(negateu(ub)))
        if u2g(u) == u2g(v):
            return (min(u, v),)
        return unifypos(ub)

def g2u(g):
    if gQ(g):
        ulo = x2u(g[0][0])
        uhi = x2u(g[0][1])
        blo = g[1][1]
        bhi = g[1][1]
        # XXX why not use the named version from above?
        if ulo == qNaNu or uhi == qNaNu or g[0][0] > g[0][1] or (g[0][0] == g[0][1] and (blo or bhi)):
            return qNaNu
        elif ulo == uhi and not (blo != bhi):
            return x2u(g[0][0])
        else:
            u1 = ubleft((g[0][0], blo))
            u2 = ubright((g[0][1], bhi))
            if u2g(unify((u1, u2))) == u2g((u1, u2)):
                return unify((u1, u2))
            else:
                return (u1, u2)

def ltgQ(g, h):
    if gQ(g) and gQ(h):
        if math.isnan(g[0][0]) or math.isnan(g[0][1]) or math.isnan(h[0][0]) or math.isnan(h[0][1]):
            return False
        return g[0][1] < h[0][0] or (g[0][1] == h[0][0] and (g[1][1] or h[1][0]))

def ltuQ(u, v):
    if uQ(u) and uQ(v):
        return ltgQ(u2g(u), u2g(v))

def gtgQ(g, h):
    if gQ(g) and gQ(h):
        if math.isnan(g[0][0]) or math.isnan(g[0][1]) or math.isnan(h[0][0]) or math.isnan(h[0][1]):
            return False
        return g[0][0] > h[0][1] or (g[0][0] == h[0][1] and (g[1][1] or h[1][0]))


def nneqgQ(g, h):
    if gQ(g) and gQ(h):
        if math.isnan(g[0][0]) or math.isnan(g[0][1]) or math.isnan(h[0][0]) or math.isnan(h[0][1]):
            return False
        return not (ltgQ(g, h) or gtgQ(g, h))

def nnequQ(u, v):
    if uQ(u) and uQ(v):
        return nneqgQ(u2g(u), u2g(v))

# Add a zero bit to the fraction length of an exact unum, if possible.
def promotef(u):
    if unumQ(u) and exQ(u):
        if fsize(u) < fsizemax:
            return 2 * (floatmask(u) & u) + (utagmask & u) + 1
        return u

# Increase the length of the exponent field of an exact unum, if possible.
def promotee(u):
    if unumQ(u) and exQ(u):
        e = expo(u)
        es = esize(u)
        f = frac(u)
        fs = fsize(u)
        s = signmask(u) & u
        ut = (utagmask & u) + fsizemax
        # If already maximum exponent size, do nothing. This also handles NaN and inf values
        if es == esizemax:
            return u
        # Take care of u = 0 case, ignoring the sign bit. It's simply the new utag.
        if e == 0 and f == u:
            return ut
        # If normal (nonzero exponent), slide sign bit left, add 2**(es-1), increment esize.
        if e > 0:
            return 2 * s + (e + 2**(es-1)) * hiddenmask(u) + ((hiddenmask(u) - 1) & u) + fsizemax
        # Subnorma. Room to shift and stay subnormal?
        if fs - (floor(log(f, 2)) + 1) >= 2**(es-1):
            return 2 * s + frac(u) * (2**(2**(es-1))) * ulpu + ut
        # Subnormal becomes normal. Trickiest case.
        # The fraction slides left such that the lefmost 1 becomes the hidden bit
        nsigbits = floor(log(f,2)) + 1
        return 2*s + (2**(es-1) + 1 - fs + nsigbits)*(hiddenmask(u)) + \
                (f - 2**nsigbits)*2**(fs-nsigbits+1)*ulpu + (utagmask & u) + fsizemask



# Promote a pair of exact unums to the same esize and fsize
def promote(u, v):
    if unumQ(u) and unumQ(v) and exQ(u) and exQ(v):
        eu = esize(u)
        ev = esize(v)
        fu = fsize(u)
        fv = fsize(v)
        ut = u
        vt = v
        while eu < ev:
            ut = promotee(ut)
            eu += 1
        while ev < eu:
            vt = promotee(vt)
            ev += 1
        while fu < fv:
            ut = promotef(ut)
            fu += 1
        while fv < fu:
            vt = promotef(vt)
            fv += 1
        return (ut, vt)

def demotee(u):
    if unumQ(u):
        es = esize(u)
        mask = int(signmask(u) / 4)
        fm = floatmask(u)
        ut = u & utagmask
        s = signmask(u) & u
        f = frac(u)
        left2 = Fraction((u & (3*mask)), mask)

        # Cannot make the exponent any smaller:
        if es == 1 or u == posinfu or u == neginfu or u == qNaNu or u == sNaNu:
            return u
        if expo(u) == 0:
            f = Fraction(f, (2**(2**(es-2))))
            ibit = ubitmask if fractionalPart(f) > 0 else 0
            # XXX: is the division ok here?
            return ibit | (s / 2 + integerPart(f) * ulpu + ut - fsizemask)
        # If the left two exponent bits are 00
        # (but it's normal, since we fell through the previous test),
        # result switches to subnormal. The exponent after the first
        # two bits joins the fraction like a fixed-point number,
        # before shifting the fraction to the right. The
        # new exponent is zero, of course.
        if left2 == 0:
            f = Fraction(2**fsize(u) + f, Fraction(2**(2**(es-2)+1), 2**expo(u)))
            ibit = ubitmask if fractionalPart(f) > 0 else 0
            return ibit | (s / 2 + integerPart(f) * ulpu + ut - fsizemask)
        # If the left two exponent bits are 01 or 10,
        # squeeze out the second bit; if that leaves a subnormal exponent,
        # shift the hidden bit and fraction bits right
        if left2 <= 2:
            e = int(((expomask(u) - 3 * mask) & u) + (u & (2*mask)) / 2)
            if e == 0:
                f = Fraction(2**fsize(u) + f, 2)
            ibit = ubitmask if fractionalPart(f) > 0 else 0
            return ibit | (int(s / 2) + e + integerPart(f) * ulpu + ut - fsizemask)
        # If the first two exponent bits are 11,
        # always get an unbounded unum, all 1s for fraction:
        return int(((u & signmask(u)) + (fm - signmask(u))) / 2) | ut - fsizemask


ubitsmoved = numbersmoved = 0

five = x2u(34.2)
def print_unum(u):
    print sign(u), expovalue(u), hidden(u), Fraction(frac(u), 2**fsize(u))
print_unum(five)
print frac(five), fsize(five)
print "numbits", numbits(five), "of", maxubits, fsize(five), "of", fsizemax, esize(five), "of", esizemax
print u2f(five)
print x2u(5)
print u2g(x2u(9005))
print plusg(u2g(x2u(34.2)), u2g(x2u(0)))
print 'result', plusu(x2u(34.2), x2u(0))
print x2u(34.2)