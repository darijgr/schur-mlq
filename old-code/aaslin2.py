# Aas & Linusson paper (arXiv:1501.04417v2).

# Multiline queues.
# This assumes that there is one new ball per row.

def movedown(cs, bos):
    # Input:
    # cs (the positions of the n-1 balls on row n-1,
    #     in the order of the numbers of the balls);
    # bos (the positions of the n holes on row n,
    #      in the order from left to right).
    # Output:
    # the positions of the n balls on row n, in the
    #     order of the numbers of the balls.
    boss = bos[:]
    bs = []
    for c in cs:
        for b in boss:
            if b >= c:
                break
            else: # wrapping around
                b = boss[0]
        boss.remove(b)
        bs.append(b)
    bs.extend(boss)
    return bs

r"""
print movedown([3], [6, 7, 8])
print movedown([6, 7, 8], [1, 2, 4, 7, 9])
print movedown([7, 9, 1, 2, 4], [1, 3, 4, 5, 6, 7, 8])
print movedown([7, 1, 3, 4, 5, 6, 8], range(1, 10))
"""

def moveups(N, bs, distinct=True):
    # Input:
    # N (the length of each row);
    # bs (the positions of the n balls on row n,
    #     in the order of the numbers of the balls).
    # Output:
    # A list of all possible cs such that
    #     movedown(N, cs, sorted(bs)) == bs.
    from itertools import product
    cranges = []
    for i, bi in enumerate(bs[:-1]):
        rel_bs = bs[i+1:]
        if rel_bs:
            if [b for b in rel_bs if b < bi]:
                lb = max(b for b in rel_bs if b < bi)
                cranges.append(range(lb + 1, bi + 1))
                continue
            lb = max(rel_bs)
            cranges.append(range(lb + 1, N) + range(bi + 1))
    it = list(product(*cranges))
    if not distinct:
        return it
    return [cs for cs in it
            if len(set(cs)) == len(cs)]

def test_moveups(N, bs):
    boss = sorted(bs)
    it = moveups(N, bs)
    if not all(movedown(iti, boss) == bs for iti in it):
        print "error 1"
        return False
        l = len(bs) - 1
    from itertools import combinations
    for cs in combinations(range(N), l):
        if movedown(cs, boss) == bs:
            if not (cs in it):
                print "error 2"
                return False
    return True

def moveupss(N, bss, distinct=True):
    return sum([moveups(N, bs, distinct=distinct) for bs in bss], [])

def mlqs(N, bs):
    # Find all MLQs of width N whose bottom row is bs.
    if len(bs) == 1:
        return [MLQ(N, [bs])]
    it = moveups(N, bs)
    res = []
    for cs in it:
        res.extend([MLQ(mlq._N, mlq._data + [bs])
                    for mlq in mlqs(N, cs)])
    return res

def pos_to_row(N, bs):
    res = [None] * N
    for i, b in enumerate(bs):
        res[b] = i
    return res

def row_to_pos(row):
    row_det = [(i, pos) for pos, i in enumerate(row) if i != None]
    row_det.sort()
    return [b[1] for b in row_det]

def mlq_to_rows(N, mlq):
    return [pos_to_row(N, bs) for bs in mlq]

def mlqs_as_rows(N, bs):
    return [mlq_to_rows(N, mlq) for mlq in mlqs(N, bs)]

# Wrapper object for latex output
class MLQ(SageObject):
    def __init__(self, N, data):
        self._N = N
        self._data = data

    def _repr_(self):
        return repr(self._data)

    def __iter__(self):
        return iter(self._data)

    def _latex_(self):
        mlq = self._data
        colors = ['red','green','blue','brown','magenta','orange','yellow']
        colors += ['black'] * (len(mlq) - len(colors))

        from sage.misc.latex import latex
        latex.add_package_to_preamble_if_available("tikz")
        ret = "\\begin{tikzpicture}[scale=1]\n"
        # We sort the rows around to be increasing
        available = [sorted(row) for row in mlq]
        n = len(mlq)
        for i in range(n):
            c = colors[i]
            x = available[i].pop()
            ret += "\\draw[->,color={c}] (-1, {i}) -- ({x}, {i})".format(c=c, i=n-i, x=x)
            for j in range(i+1, n):
                ret += "-- ({x}, {j})".format(x=x, j=n-j)
                row = available[j]
                if row[-1] >= x:
                    for k in range(len(row)):
                        if row[k] >= x:
                            x = row.pop(k)
                            break
                    ret += "-- ({x}, {j})".format(x=x, j=n-j)
                else:
                    x = row.pop(0)
                    ret += "-- ({N}, {j});\n\\draw[->,color={c}] (-1, {j}) -- ({x}, {j})".format(N=self._N, c=c, j=n-j, x=x)
            ret += "-- ({x}, 0);\n".format(x=x)
        for i, row in enumerate(mlq):
            for j in row:
                ret += "\\draw[fill=white] ({j}, {i}) circle (.15);\n".format(i=n-i, j=j)
        ret += "\\end{tikzpicture}"
        return ret

def test_p37(N, bs):
    # Check Proposition 3.7.
    # The bs should be strictly decreasing.
    bsr = list(reversed(bs))
    n = len(bs)
    M = Matrix(QQ, [[binomial(bsr[i] + j, j) for j in range(n)]
                    for i in range(n)])
    return len(mlqs(N, bs)) == M.det()

def allowed_permutations(bs, ks):
    # Input:
    # bs (a list of n integers);
    # ks (a strictly decreasing list of elements of
    #     {1, 2, ..., n-1}).
    # Output:
    # the list of all permutations of bs induced by the
    # Young subgroup of the symmetric group S_n generated by
    # s_k, where k ranges over all entries of ks.
    from itertools import permutations
    n = len(bs)
    Sn = SymmetricGroup(n)
    s = Sn.simple_reflections()
    YS = [Permutation(p) for p in Sn.subgroup([s[k] for k in ks])]
    #print YS
    return [[bs[p[i]-1] for i in range(n)]
            for p in YS]

def test_c310(N, bs, ks):
    # Check Conjecture 3.10.
    # Input:
    # The bs should be strictly decreasing.
    # The ks should be strictly decreasing, or better.
    n = len(bs)
    bsr = list(reversed(bs))
    k_par = Partition(ks)
    k_par_prime = list(reversed(k_par.conjugate()))
    k_par_prime = [0] * (n - len(k_par_prime)) + k_par_prime
    M = Matrix(QQ, [[binomial(bsr[i] + j - k_par_prime[i], bsr[i]) for j in range(n)]
                    for i in range(n)])
    print "k' (reversed) is ", k_par_prime
    print "we are taking the determinant of \n", M
    dM = M.det()
    rhs = dM * prod(binomial(N, ki) for ki in ks)
    lhs = 0
    from itertools import combinations
    for bs_permuted in allowed_permutations(bs, ks):
        print "currently attacking last row ", bs_permuted
        lhs += len(mlqs(N, bs_permuted))
    print "lhs ", lhs
    print "rhs ", rhs
    if lhs == rhs:
        return True
    return False
    
def genfun(N, bs, ks):
    # Generating function for the MLQs
    # with given bottom row bs and width N,
    # weighted by spectral parameters.
    P = PolynomialRing(QQ, 'x', N)
    xs = P.gens()
    lhs = P.zero()
    from itertools import combinations
    for bs_permuted in allowed_permutations(bs, ks):
        print "currently attacking last row ", bs_permuted
        for mlq in mlqs(N, bs_permuted):
            lhs += P.prod(xs[i] for row in mlq for i in row)
    return lhs

r"""
Today's loot:

We believe that test_c310 holds for every strictly
decreasing ks (not just the ones where the entries
are separated).
We suspect that there is a generating-function lift
where the determinants become something like flagged
Schur functions (not literally, maybe),
and the product of the (N choose k_i) becomes a product
of e_{k_i} (x_1, x_2, ..., x_N).
Something like the flagged Schur function for
\lambda_i = i + k_{n+1-i}(S)' (the partition)
and row-maxima b_1, b_2, ..., b_n.
If ks == [], then genfun(N, bs, ks) seems to be the
genfun of semi-strict Gelfand-Tsetlin patterns with
top row bs.
# http://alistairsavage.ca/pubs/Rakotoarisoa-ice-models.pdf

"""

def test_c310x(N, bs, ks):
    # OBSOLETE -- this guess was wrong.
    # Check Conjecture 3.10x.
    # Input:
    # The bs should be strictly decreasing.
    # The ks should be strictly decreasing, or better.
    lhs = genfun(N, bs, ks)
    P = lhs.parent()
    xs = P.gens()
    n = len(bs)
    bsr = list(reversed(bs))
    k_par = Partition(ks)
    k_par_prime = list(reversed(k_par.conjugate()))
    k_par_prime = [0] * (n - len(k_par_prime)) + k_par_prime
    print "k' (reversed) is ", k_par_prime
    # M = Matrix(P, [[binomial(bsr[i] + j - k_par_prime[i], bsr[i]) for j in range(n)]
    #                for i in range(n)])
    # I need to modify this matrix.
    # print "we are taking the determinant of \n", M
    # dM = M.det()
    # We don't know what matrix to take the determinant of.
    # But we have the following tableau-theoretical
    # interpretation:
    # They are the generating function for semistandard
    # tableaux of "skew shape" (1, 2, ..., n) / k_par_prime
    # (not an actual skew partition, but an upside-down one
    # (Joel thinks it can be reinterpreted as a shifted skew
    # shape, by the way))
    # whose diagonal entries are bs[0], bs[1], ..., bs[n-1].
    dM = P.zero()
    def weight_prod(T):
        return P.prod(xs[num]
                      for row in T for num in row if not (num is None))
    T = [[None] * k_par_prime[i] + [bsr[i]] * (i + 1 - k_par_prime[i])
         for i in range(n)]
    while True:
        print "tableau detected:"
        for row in T:
            print [(num if not (num is None) else 0) for num in row]
        print "its weight product is ", weight_prod(T)
        dM += weight_prod(T)
        lowerable = False
        for i in reversed(range(1, n)):
            Ti = T[i]
            Ti_1 = T[i-1]
            for j in reversed(range(k_par_prime[i], i)):
                Tij = Ti[j]
                if Tij <= Ti_1[j] + 1:
                    continue # This also prevents Tij from getting < 1.
                if j > 0 and Ti[j-1] == Tij:
                    continue
                lowerable = True
                Ti[j] -= 1
                # Having lowered T[i][j], we reset all later values to
                # their maximal possible values.
                Ti[j+1 : i+1] = [bsr[i]] * (i-j)
                for k in range(i+1, n):
                    T[k] = [None] * k_par_prime[k] + [bsr[k]] * (k + 1 - k_par_prime[k])
                break
            if lowerable:
                break
        else:
            break # We found all tableaux.
    # Now to the product of elementary symmetric functions:
    from itertools import combinations
    ellprod = P.prod(P.sum(P.prod(x for x in xsub)
                           for xsub in combinations(xs, ki))
                     for ki in ks)
    rhs = dM * ellprod
    print "lhs / ellprod - dM =", lhs / ellprod - dM
    if lhs == rhs:
        return True
    return False

def test_c310x2(N, bs, ks):
    # OBSOLETE -- this guess was wrong.
    # Check Conjecture 3.10x2.
    # Input:
    # The bs should be strictly decreasing.
    # The ks should be strictly decreasing, or better.
    lhs = genfun(N, bs, ks)
    P = lhs.parent()
    xs = P.gens()
    n = len(bs)
    bsr = list(reversed(bs))
    k_par = Partition(ks)
    k_par_prime = list(reversed(k_par.conjugate()))
    k_par_prime = [0] * (n - len(k_par_prime)) + k_par_prime
    print "k' (reversed) is ", k_par_prime
    # M = Matrix(P, [[binomial(bsr[i] + j - k_par_prime[i], bsr[i]) for j in range(n)]
    #                for i in range(n)])
    # I need to modify this matrix.
    # print "we are taking the determinant of \n", M
    # dM = M.det()
    # We don't know what matrix to take the determinant of.
    # But we have the following tableau-theoretical
    # interpretation:
    # They are the generating function for semistandard
    # tableaux of "skew shape" (1, 2, ..., n) / k_par_prime
    # (not an actual skew partition, but an upside-down one
    # (Joel thinks it can be reinterpreted as a shifted skew
    # shape, by the way))
    # whose diagonal entries are bs[0], bs[1], ..., bs[n-1].
    dM = P.zero()
    def weight_prod(T):
        return P.prod(xs[num]
                      for row in T for num in row if not (num is None))
    T = [[None] * k_par_prime[i] + [bsr[i]] * (i + 1 - k_par_prime[i])
         for i in range(n)]
    while True:
        print "tableau detected:"
        for row in T:
            print [(num if not (num is None) else 0) for num in row]
        print "its weight product is ", weight_prod(T)
        dM += weight_prod(T)
        lowerable = False
        for i in reversed(range(1, n)):
            Ti = T[i]
            Ti_1 = T[i-1]
            for j in reversed(range(k_par_prime[i], i)):
                Tij = Ti[j]
                if Tij <= Ti_1[j] + 1:
                    if Tij <= Ti_1[j] or k_par_prime[i] == k_par_prime[i-1] or (j > 0 and Ti_1[j-1] == Ti_1[j]):
                        continue # This also prevents Tij from getting < 1.
                if j > 0 and Ti[j-1] == Tij:
                    continue
                lowerable = True
                Ti[j] -= 1
                # Having lowered T[i][j], we reset all later values to
                # their maximal possible values.
                Ti[j+1 : i+1] = [bsr[i]] * (i-j)
                for k in range(i+1, n):
                    T[k] = [None] * k_par_prime[k] + [bsr[k]] * (k + 1 - k_par_prime[k])
                break
            if lowerable:
                break
        else:
            break # We found all tableaux.
    # Now to the product of elementary symmetric functions:
    from itertools import combinations
    ellprod = P.prod(P.sum(P.prod(x for x in xsub)
                           for xsub in combinations(xs, ki))
                     for ki in ks)
    rhs = dM * ellprod
    print "\nlhs / ellprod - dM =", lhs / ellprod - dM
    if lhs == rhs:
        return True
    return False

def complete_symm(R, xs, k):
    # The ``k``-th complete homogeneous symmetric function
    # in the ``xs``, as element of ring ``R``.
    if k < 0:
        return R.zero()
    from itertools import combinations_with_replacement
    return R.sum(R.prod(combination)
                        for combination in combinations_with_replacement(xs, k))

def flagged_schur(R, lam, bs):
    # Flagged Schur function for a straight shape ``lam``
    # with flag ``bs``.
    # Note that ``bs`` has to be at least as long as ``lam``.
    # R = PolynomialRing(QQ, 'x', max(bs + [0]))
    # xs = R.gens()
    xs = R.gens()
    lam_list = list(lam)
    n = len(lam_list)
    if len(bs) > n:
        bs = bs[:n]
    M = Matrix(R, [[complete_symm(R, xs[:bs[i]], lam_list[i] - i + j)
                    for i in range(n)] for j in range(n)])
    return M.det()

def test_c310f(N, bs, ks):
    # OBSOLETE -- this guess was wrong.
    # Check Conjecture 3.10f.
    # Input:
    # The bs should be strictly decreasing.
    # The ks should be strictly decreasing, or better.
    lhs = genfun(N, bs, ks)
    P = lhs.parent()
    xs = P.gens()
    n = len(bs)
    bsr = list(reversed(bs))
    k_par = Partition(ks)
    k_par_prime = list(reversed(k_par.conjugate()))
    k_par_prime = [0] * (n - len(k_par_prime)) + k_par_prime
    print "k' (reversed) is ", k_par_prime
    osh = [n - i - k_par_prime[i] for i in range(n)]
    bs_rev = list(reversed(bs))
    flags = bs_rev
    #flags = [b + 1 for b in bs_rev]
    print osh, flags
    dM = flagged_schur(P, osh, flags)
    # Now to the product of elementary symmetric functions:
    from itertools import combinations
    ellprod = P.prod(P.sum(P.prod(x for x in xsub)
                           for xsub in combinations(xs, ki))
                     for ki in ks)
    print (dM, ellprod, lhs)
    rhs = dM * ellprod
    print "\nlhs / ellprod - dM =", lhs / ellprod - dM
    if lhs == rhs:
        return True
    return False

def test_c310jt(N, bs, ks):
    # Check Conjecture 3.10jt.
    # Input:
    # The bs should be strictly decreasing.
    # The ks should be strictly decreasing, or better.
    lhs = genfun(N, bs, ks)
    P = lhs.parent()
    xs = P.gens()
    n = len(bs)
    bsr = list(reversed(bs))
    k_par = Partition(ks)
    k_par_prime = list(reversed(k_par.conjugate()))
    k_par_prime = [0] * (n - len(k_par_prime)) + k_par_prime
    print "k' (reversed) is ", k_par_prime
    print "the partition shape is ", [i - k_par_prime[i] for i in range(n)]
    N = [[(bsr[i] + 1, - k_par_prime[i] + j)
                    for j in range(n)] for i in range(n)]
    for row in N:
        print row
    M = Matrix(P, [[complete_symm(P, xs[: bsr[i] + 1], - k_par_prime[i] + j)
                    for j in range(n)] for i in range(n)])
    dM = M.det()
    # Now to the product of elementary symmetric functions:
    from itertools import combinations
    ellprod = P.prod(P.sum(P.prod(x for x in xsub)
                           for xsub in combinations(xs, ki))
                     for ki in ks)
    # Finally, multiply with a stupid monomial.
    rhs = dM * ellprod * P.prod(xs[i] for i in bs)
    # print "\nlhs / ellprod - dM =", lhs / ellprod - dM
    if lhs == rhs:
        return True
    return False

