import numpy as np
from time import time
# taken from https://github.com/HoBeom/OneEuroFilter-Numpy
def smoothing_factor(t_e, cutoff):
    r = 2 * np.pi * cutoff * t_e
    return r / (r + 1)


def exponential_smoothing(a, x, x_prev):
    return a * x + (1 - a) * x_prev


class OneEuroFilter:
    """
    One Euro Filter for smoothing signals, taken from https://github.com/HoBeom/OneEuroFilter-Numpy

    Examples
    --------
    ```
    >>> from fast_cody import OneEuroFilter
    >>> import numpy as np
    >>> mu = np.ones((3, 1))
    >>> x0 =  np.random.randn(3, 1) + mu
    >>> f = OneEuroFilter(x0)
    >>> x = np.random.randn(3, 1) + mu
    >>> x_filtered = f(x)
    >>> print(x_filtered)
    ```
    """
    def __init__(self, x0, dx0=0.0, min_cutoff=1.0, beta=0.0,
                 d_cutoff=1.0):
        """Initialize the one euro filter.

        Parameters
        ----------
        x0 : float
            Initial value for the filtered signal.
        dx0 : float
            Initial value for the derivative.
        min_cutoff : float
            Minimum cutoff frequency.
        beta : float
            Cutoff slope.
        d_cutoff : float
            Cutoff frequency for the derivate.

        """
        # The parameters.
        self.data_shape = x0.shape
        self.min_cutoff = np.full(x0.shape, min_cutoff)
        self.beta = np.full(x0.shape, beta)
        self.d_cutoff = np.full(x0.shape, d_cutoff)
        # Previous values.
        self.x_prev = x0.astype(float)
        self.dx_prev = np.full(x0.shape, dx0)
        self.t_prev = time()

    def __call__(self, x):
        """Compute the filtered signal."""
        assert x.shape == self.data_shape

        t = time()
        t_e = t - self.t_prev
        t_e = np.full(x.shape, t_e)

        # The filtered derivative of the signal.
        a_d = smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = exponential_smoothing(a_d, dx, self.dx_prev)

        # The filtered signal.
        cutoff = self.min_cutoff + self.beta * np.abs(dx_hat)
        a = smoothing_factor(t_e, cutoff)
        x_hat = exponential_smoothing(a, x, self.x_prev)

        # Memorize the previous values.
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat