# from https://git.sagemath.org/sage.git/tree/src/sage/crypto/linearlayer.py?h=u/asante/linear_layer_module&id=9155aa93f62e2c1bab51a095137b62367c1e7fbb
# (but doctest were removed because otherwise sage runs them when importing
# this module)

from six import integer_types

from sage.combinat.permutation import Permutation
from sage.matrix.constructor import Matrix
from sage.matrix.matrix_mod2_dense import Matrix_mod2_dense
from sage.matrix.matrix_gf2e_dense import Matrix_gf2e_dense
from sage.misc.cachefunc import cached_method
from sage.modules.free_module_element import vector
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

from sage.misc.superseded import experimental

from sage.structure.sage_object import SageObject

import sys


def branch_number(mtr):
    """
    Comput the branch number of the given matrix
    """
    from sage.coding.linear_code import LinearCode
    from sage.matrix.special import identity_matrix

    F = mtr.base_ring()
    n = mtr.nrows()
    id = identity_matrix(F, n)
    generator_matrix = Matrix(F, [list(a) + list(b) for a, b in zip(id, mtr)])
    return LinearCode(generator_matrix).minimum_distance()


def ff_elem_to_binary(elem):
    """
    Convert a finite field element to a binary matrix carrying out the according
    multiplication
    """
    from sage.matrix.special import companion_matrix, identity_matrix, zero_matrix

    F = elem.parent()
    R = companion_matrix(F.modulus(), format='right')
    bits = ZZ(elem.integer_representation()).digits(base=2, padto=F.degree())
    result = zero_matrix(GF(2), F.degree())
    T = identity_matrix(GF(2), F.degree())
    for i in bits:
        if i == 1:
            result += T
        T = T*R
    return result


def ff_matrix_to_binary(mtr):
    """
    Convert a matrix over a finite field to a binary matrix carrying out the
    according multiplication
    """
    from sage.matrix.special import block_matrix

    result = []
    for row in mtr:
        for elem in row:
            result.append(ff_elem_to_binary(elem))
    return block_matrix(mtr.nrows(), mtr.ncols(), result)


def column_linear_layer(Ls):
    """
    Return the linear layer that applies a given linear layer ``L`` to ``ncols``
    in parallel.

    The most common application for this is, to build the matrix that applies the
    AES MixColumns linear layer to each column of a state, while the state is
    represented as a vector.
    """
    from sage.matrix.special import block_matrix, diagonal_matrix

    F = Ls[0].base_ring()
    nblocks = len(Ls)
    n, m = Ls[0].dimensions()
    blockmtrs = [diagonal_matrix(F, nblocks, [Ls[i][k][l]
                                              for i in range(nblocks)])
                 for k in range(n)
                 for l in range(m)]
    return LinearLayer.new(block_matrix(F, n, m, blockmtrs))


class LinearLayer(SageObject):
    @staticmethod
    def new(*args,  **kwargs):
        """
        Construct a linear layer for a given matrix `L` of dimension m x n.

        INPUT:

        - ``L`` - a matrix representing the linear layer part.
       """
        def LinearLayerFactory(K):
            if K.characteristic() == 2 and K.degree() == 1:
                return type("LinearLayerGF2", (LinearLayer, Matrix_mod2_dense), {})
            if K.characteristic() == 2 and K.degree() >= 1:
                return type("LinearLayerGF2E", (LinearLayer, Matrix_gf2e_dense), {})
            else:
                raise NotImplementedError

        if "L" in kwargs:
            L = kwargs["L"]
        elif len(args) == 1:
            L = args[0]
        else:
            raise TypeError("No matrix L as argument provided.")

        parent = L.parent()
        base_ring = L.base_ring()
        return LinearLayerFactory(base_ring)(parent, L)

    def _latex_(self):
        r"""
        Return a `LaTeX` version of the operation table as a string,
        using a `LaTeX` ``array`` environment.
        """

        return "x \\ {\\mapsto} " + self.matrix()._latex_() + " {\\cdot} \\ x"

    def __str__(self):
        return "LinearLayer of dimension %d x %d represented as\n%s" \
               % (self.dimensions() + (self.matrix().str(),))

    def __repr__(self):
        return "LinearLayer of dimension %d x %d represented as\n%s" \
               % (self.dimensions() + (self.matrix().__repr__(),))

    def matrix(self):
        """
        Return the matrix representing this linear layer
        """
        return self.parent(self._matrix_())

    def binary_matrix(self):
        """
        Return the matrix representing this linear layer in it's binary
        representation
        """
        if self.base_ring() is GF(2):
            # this originally did not return
            # <class 'sage.matrix.matrix_mod2_dense.Matrix_mod2_dense'>
            # but <class 'sage.all_cmdline.LinearLayerGF2'>
            # which is kind of unexpected? and so i changed it
            return Matrix(GF(2), self._matrix_())
        return ff_matrix_to_binary(self._matrix_())

    def __call__(self, x):
        """
        Apply linear layer to ``x``.

        INPUT:

        - ``x`` - either an integer, a tuple of `GF{2}` elements of
          length ``len(self)`` or a finite field element in
          `GF{2^n}`. As a last resort this function tries to convert
          ``x`` to an integer.
        """
        from sage.modules.free_module_element import FreeModuleElement

        if isinstance(x, integer_types + (Integer,)):
            x = vector(GF(2), ZZ(x).digits(base=2, padto=self.ncols()))
            return ZZ(list(self.binary_matrix() * x), 2)

        elif isinstance(x, tuple):
            if len(x) != self.ncols():
                raise TypeError("Cannot apply LinearLayer to provided element, "
                                "dimension mismatch")

            try:
                x = vector(self.matrix().base_ring(), x)
            except (TypeError, ZeroDivisionError):
                raise TypeError("Cannot apply LinearLayer to provided element %r, "
                                "conversion to vector failed" % (x,))

            return tuple(self * x)

        elif isinstance(x, list):
            if len(x) != self.ncols():
                raise TypeError("Cannot apply LinearLayer to provided element, "
                                "dimension mismatch")

            try:
                x = vector(self.base_ring(), x)
            except (TypeError, ZeroDivisionError):
                raise TypeError("Cannot apply LinearLayer to provided element %r, "
                                "conversion to vector failed" % (x,))

            return list(self * x)

        elif isinstance(x, FreeModuleElement):
            return self * x

        else:
            raise TypeError("Unsupported type for input x: %s" % type(x))

    def is_permutation(self):
        r"""
        Check if the linear layer is a permutation, i.e., if the representing
        matrix is a permutation.
        """
        # a permutation matrix has to be a square
        if not self.is_square():
            return False

        # in each row, all entries execpt one should be 0, the other should be 1
        for r in self.rows():
            if r.hamming_weight() != 1:
                return False
            if r[r.nonzero_positions()[0]] != 1:
                return False

        # in each column, all entries execpt one should be 0, the other should be 1
        for c in self.columns():
            if c.hamming_weight() != 1:
                return False
            if c[c.nonzero_positions()[0]] != 1:
                return False

        return True

    def xor_count(self, algorithm="naive"):
        """
        Count the number of xor operations needed for a naive implementation

        INPUT:

        - ``algorithm`` - string choosing which algorithm to use to compute
            the xor count. Available algorithms

            - 'naive' - non-optimized implementation (default)
        """
        avail_algs = ["naive"]
        if algorithm not in avail_algs:
            raise TypeError("algorithm must be one of %s" % avail_algs)

        if algorithm == "naive":
            mtr = self.binary_matrix()
            n, m = mtr.dimensions()
            return mtr.density() * n * m - n

    @cached_method
    def differential_branch_number(self):
        """
        Compute the differential branch number of the linear layer
        """
        if self.is_permutation():
            return 2
        return branch_number(self.matrix())

    @cached_method
    def linear_branch_number(self):
        """
        Compute the linear branch number of the linear layer
        """
        if self.is_permutation():
            return 2
        return branch_number(self.matrix().transpose())


class AESLikeLinearLayer(LinearLayer, Matrix_gf2e_dense):
    r"""
    An AES like linear layer consists of ShuffleCells and MixColumns matrices,
    corresponding to the linear layer structure used in the AES.

    Here, ShuffleCells is either a Permutation object, or a permutation matrix,
    and MixColumns any arbitrary matrix.
    """
    @staticmethod
    def new(sc, mc, apply_columns=True):
        """
        Construct an AES linear layer for a given matrix `L` of dimension m x n.

        INPUT:

        - ``sc`` - a permutation or matrix representing the ShuffleCells part
        - ``mc`` - a matrix representing the MixColumns part
        - ``apply_columns`` - Bool; wether to apply MixColumns column-wise (default)
            or row-wise
        """
        K = mc.base_ring()
        if not (K.characteristic() == 2 and K.degree() >= 2):
            raise NotImplementedError

        if isinstance(sc, Permutation):
            sc = Matrix(K, sc.to_matrix())

        m = Matrix(K, column_linear_layer([mc]*mc.ncols()))*sc
        if not apply_columns:
            raise NotImplementedError

        ll = AESLikeLinearLayer(m.parent(), m)
        ll._sc = sc
        ll._mc = mc
        ll._apply_columns = apply_columns

        return ll

    def __repr__(self):
       # convert ShuffleCells permutation matrix to a permutation object
        perm_sc = Permutation(map(lambda x: 1+list(x).index(1), self._sc.columns()))
        n, m = self.dimensions()
        degree = self.base_ring().degree()
        return ("AES like LinearLayer of dimension %d x %d represented by "
                "ShuffleCells\n%s\nand MixColumns\n%s" \
                % (n*degree, m*degree, perm_sc, self._mc))

    @cached_method
    def differential_branch_number(self):
        """
        Computes the differential branch number of the MixColumn Matrix
        """
        M = self._mc
        return branch_number(M)

    @cached_method
    def linear_branch_number(self):
        """
        Computes the linear branch number of the MixColumn Matrix
        """
        M = self._mc
        M = M.transpose()
        return branch_number(M)

    def vector_to_state(self, v, column_wise=None):
        """
        Converts the given vector ``v`` to a state matrix.

        INPUT:

            - ``v`` -- a vector
            - ``column_wise -- Bool; wether to fill the state matrix column
                wise, or row wise (defaults to ``apply_columns`` initialised
                value)

        The state's dimension is `n \\times m` where the number of rows `n` is
        determined by the MixColumn matrix and the number of columns `m` is the
        length of the ShuffleCell permutation (or equivalently the dimension of
        its matrix) divided by the number of rows.

        By default the state matrix is filled column wise, if the MixColumn
        matrix is also applied column wise, but this can also be controlled
        with the ``column_wise`` flag.
        """
        from sage.matrix.special import column_matrix

        if column_wise is None:
            column_wise = self._apply_columns

        n = self._mc.nrows()
        m = self._sc.nrows() // n

        if column_wise:
            state = column_matrix(self.base_ring(), m, n, list(v))
        else:
            state = Matrix(self.base_ring(), n, m, list(v))

        return state

    def state_to_vector(self, s, column_wise=None):
        """
        Converts the given state matrix ``s`` to a vector.

        INPUT:

            - ``s`` -- a matrix
            - ``column_wise -- Bool; wether to fill the state matrix column
                wise, or row wise (defaults to ``apply_columns`` initialised
                value)

        By default the vector is filled column wise from the state matrix, if
        the MixColumn matrix is also applied column wise, but this can also be
        controlled with the ``column_wise`` flag.
        """
        if column_wise is None:
            column_wise = self._apply_columns

        if column_wise:
            v = s.transpose().list()
        else:
            v = s.list()

        return vector(self.base_ring(), v)

    def __call__(self, x):
        from sage.matrix.matrix_gf2e_dense import Matrix_gf2e_dense

        # TODO: how to call the LinearLayer.__call__ method without creating
        #       a new LinearLayer object?
        if isinstance(x, Matrix_gf2e_dense):
            y = LinearLayer.new(self.matrix())(self.state_to_vector(x))
            return self.vector_to_state(y)
        else:
            return LinearLayer.new(self.matrix())(x)


# swapped in original version
Right_ShiftRows = Permutation([1, 6, 11, 16, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12])
Left_ShiftRows = Permutation([1, 14, 11, 8, 5, 2, 15, 12, 9, 6, 3, 16, 13, 10, 7, 4])

_AES_irreducible_polynomial = PolynomialRing(GF(2), name="a")("a^8 + a^4 + a^3 + a + 1")
_AES_field = GF(2**8, name="x", modulus=_AES_irreducible_polynomial, repr="int")
AES_ShiftRows = Left_ShiftRows
AES_MixColumns = Matrix(_AES_field, 4, 4,
    map(_AES_field.fetch_int, [2, 3, 1, 1, 1, 2, 3, 1, 1, 1, 2, 3, 3, 1, 1, 2]))
AES = AESLikeLinearLayer.new(AES_ShiftRows, AES_MixColumns)

Midori_ShuffelCells = Permutation([1, 11, 6, 16, 15, 5, 12, 2,
                                   10, 4, 13, 7, 8, 14, 3, 9])
Midori_MixColumns = Matrix(GF(2**4, repr="int"),
    [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]])
Midori = AESLikeLinearLayer.new(Midori_ShuffelCells, Midori_MixColumns)

SKINNY_ShiftRows = Right_ShiftRows
SKINNY_4_MixColumns = Matrix(GF(2**4, repr="int"),
    [[1, 0, 1, 1], [1, 0, 0, 0], [0, 1, 1, 0], [1, 0, 1, 0]])
SKINNY_8_MixColumns = Matrix(GF(2**8, repr="int"),
    [[1, 0, 1, 1], [1, 0, 0, 0], [0, 1, 1, 0], [1, 0, 1, 0]])
SKINNY_4 = AESLikeLinearLayer.new(SKINNY_ShiftRows, SKINNY_4_MixColumns)
SKINNY_8 = AESLikeLinearLayer.new(SKINNY_ShiftRows, SKINNY_8_MixColumns)


def smallscale_present_linearlayer(nsboxes=16):
    """
    The matrix representing SmallPRESENT with nsboxes many S-boxes.

    INPUT:

    - ``nsboxes`` - integer, number of sboxes the linear layer operates on
      (default: 16).
    """
    from sage.modules.free_module import VectorSpace

    def present_llayer(n, x):
        dim = 4*n
        y = [0]*dim
        for i in range(dim-1):
            y[i] = x[(n * i) % (dim - 1)]
        y[dim-1] = x[dim-1]
        return vector(GF(2), y)

    m = Matrix(GF(2), [present_llayer(nsboxes, ei)
                       for ei in VectorSpace(GF(2), 4*nsboxes).basis()])
    return LinearLayer.new(m)


PRESENT = smallscale_present_linearlayer(nsboxes=16)


GIFT64 = LinearLayer.new(Matrix(GF(2), Permutation([
    1, 18, 35, 52, 49, 2, 19, 36, 33, 50, 3, 20, 17, 34, 51, 4,
    5, 22, 39, 56, 53, 6, 23, 40, 37, 54, 7, 24, 21, 38, 55, 8,
    9, 26, 43, 60, 57, 10, 27, 44, 41, 58, 11, 28, 25, 42, 59, 12,
    13, 30, 47, 64, 61, 14, 31, 48, 45, 62, 15, 32, 29, 46, 63, 16
    ]).to_matrix()))

GIFT128 = LinearLayer.new(Matrix(GF(2), Permutation([
    1, 34, 67, 100, 97, 2, 35, 68, 65, 98, 3, 36, 33, 66, 99, 4,
    5, 38, 71, 104, 101, 6, 39, 72, 69, 102, 7, 40, 37, 70, 103, 8,
    9, 42, 75, 108, 105, 10, 43, 76, 73, 106, 11, 44, 41, 74, 107, 12,
    13, 46, 79, 112, 109, 14, 47, 80, 77, 110, 15, 48, 45, 78, 111, 16,
    17, 50, 83, 116, 113, 18, 51, 84, 81, 114, 19, 52, 49, 82, 115, 20,
    21, 54, 87, 120, 117, 22, 55, 88, 85, 118, 23, 56, 53, 86, 119, 24,
    25, 58, 91, 124, 121, 26, 59, 92, 89, 122, 27, 60, 57, 90, 123, 28,
    29, 62, 95, 128, 125, 30, 63, 96, 93, 126, 31, 64, 61, 94, 127, 32
    ]).to_matrix()))


# Dictionary of all available linear layers
linearlayers = {}
for k in dir(sys.modules[__name__]):
    v = getattr(sys.modules[__name__], k)
    if isinstance(v, (LinearLayer, AESLikeLinearLayer)):
        linearlayers[k] = v

