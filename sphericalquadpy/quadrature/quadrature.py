"""Quadrature is an abstract class which defines
the interface for every derived quadrature."""
import types
from abc import ABCMeta, abstractmethod
from numpy import zeros, dot


class Quadrature(metaclass=ABCMeta):
    """Abstract Quadrature class"""

    @abstractmethod
    def computequadpoints(self, order):
        """
        Computes the quadrature points based on a given order.

        Args:
            order: The quadrature order.
        Returns:
            quadraturepoints: An (n,3) numpy.ndarray of spherical points
            living on the unit sphere.
        """

    @abstractmethod
    def computequadweights(self, order):
        """
        Computes the quadrature weights based on a given order.

        Args:
            order: The quadrature order.
        Returns:
            quadraturepoints: An (n) numpy.ndarray of weights that sum to 4pi.
        """

    @abstractmethod
    def nqbyorder(self, order):
        """
        Specifies how the order relates to the number of quadrature points.

        Args:
            order: The quadrature order.
        Returns:
            nquadpoints: The resulting number of quadrature points if choosing
            the specified order.
        """

    def __init__(self, **kwargs):
        """The init method sets xyz (the quadrature points) and weights
        (the quadrature weights) based on the implementation of the
        computequadpoints and computequadweights methods.
        There can be exactly one keyword given, either order=something
        or nq=something.
        If nq is specified, we choose the order according to
        getcorrespondingorder.
        """
        if not len(kwargs) == 1:
            raise ValueError("Exactly one keyword has to be given.")

        order = None
        if "order" in kwargs:
            order = kwargs["order"]
        elif "nq" in kwargs:
            nq = kwargs["nq"]
            order = self.getcorrespondingorder(nq)
        else:
            raise ValueError("Keyword has to be order or nq.")

        if order < 0:
            raise ValueError("Order can not be negative")

        self.xyz = self.computequadpoints(order)
        self.weights = self.computequadweights(order)

    def integrate(self, functions):
        """Integrate an array of functions with the given quadrature.
        It is assumed that every function has the signature f(x,y,z), i.e.
        takes three inputs and returns one scalar output.
        Args:
            functions: An array of functions or a single function
        Returns:
            integral: An array (if an array of functions is given as input)
            that contains the approximation of the integral
            of the respective function via the specified quadrature.

        """
        if isinstance(functions, types.FunctionType):  # no array of functions
            return dot(
                self.weights, functions(self.xyz[:, 0], self.xyz[:, 1], self.xyz[:, 2])
            )

        # if we have an array of functions proceed here:
        results = zeros(len(functions))
        for i, func in enumerate(functions):
            results[i] = dot(
                self.weights, func(self.xyz[:, 0], self.xyz[:, 1], self.xyz[:, 2])
            )
        return results

    def getcorrespondingorder(self, nquadpoints_desired):
        """If the user specifies the number of quadrature points,
        then we compute the order, such that it is the highest order
        that yields a number of quadrature points which is smaller or equal
        than the demanded number of quadrature points."""
        order = 1
        while self.nqbyorder(order + 1) <= nquadpoints_desired:
            order += 1
        return order
