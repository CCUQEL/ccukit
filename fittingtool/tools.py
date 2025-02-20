""" General tools for fitting, that will be imported when `import ccukit.fittingtool`.

functions:
-- circle_fit: 還沒寫
-- r2_score: Evaluate the R-squred value
-- fit_and_plot: Fit x-y data and plot it. Returns fitted coefficients and R^2 value.

Developer should add new function/class/object name in the `__all__` list.
"""

import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
#from sklearn.metrics import r2_score
import inspect

__all__ = [
    'fit_and_plot',
    'circle_fit',
    'r2_score'
]

def circle_fit():
    """寫ㄚ"""
    return "還想circle fit, 自己寫ㄚ"

def r2_score(y_true, y_pred):
    """Evaluate the R-squred value."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

def fit_and_plot(x_data,
                 y_data,
                 func,
                 *,
                 strpts = None,
                 bds = (-np.inf, np.inf),
                 guess_mode = False,
                 print_result = True):
    """Fit x-y data and plot it. Returns fitted coefficients and R^2 value.

    Example usage:
    >>> from ccukit import fit_and_plot
    >>> import numpy as np
    >>>  
    >>> def linear(x, a, b, c):
    >>>     return a*x**2 + b*x + c
    >>> x_data = np.array([1, 2, 3, 4, 5, 6])
    >>> y_data = np.array([1.1, 2.4, 3.2, 4, 5.4, 7])
    >>> strpts = [1, 1, 0.2] # a, b, c
    >>> bds = ([0, 0, 0], [10, 10, 10]) # lowers, uppers
    >>> coeffs, Rsquared = fit_and_plot(
    >>>     x_data,
    >>>     y_data,
    >>>     linear,
    >>>     strpts=strpts,
    >>>     bds=bds,
    >>>     guess_mode=True, # guess untill the strpts is a close enough
    >>>     print_result=True
    >>> )

    For guess mode, it plot the guessed function along with data.

    Returns:
    coeffs, Rsquared:
    -- coeffs(tuple): the fitted coefficients
    -- Rsquared(float): the R^2 value.
    (returns None, None in guess mode)
    """

    if guess_mode:
        plt.plot(x_data, y_data, 'k s', label='data')
        samt = np.linspace(np.min(x_data), np.max(x_data), 200)
        plt.plot(samt, func(samt, *strpts), label='guess')
        plt.legend()
        plt.grid()
        plt.show()
        return None, None
    # fitting
    if not guess_mode:
        coeffs, cov = curve_fit(func,
                                x_data,
                                y_data,
                                p0=strpts,
                                bounds=bds)

        # print fitted result
        if print_result:
            param_names = list(inspect.signature(func).parameters.keys())[1:]
            print('fitted result:')
            for name, value in zip(param_names, coeffs):
                print(f">> {name} = {value:.5f}")
            y_pred = func(x_data, *coeffs)
            Rsquared = r2_score(y_data, y_pred)
            print(f'with R-squared value R^2 = {Rsquared:.5f}')

        # plot
        plt.plot(x_data, y_data, 'k s', label='data')
        samx = np.linspace(np.min(x_data), np.max(x_data), 200)
        plt.plot(samx, func(samx, *coeffs), 'r-',label='fitted')
        plt.xlim(np.min(x_data), np.max(x_data))
        plt.legend()
        plt.grid()
        plt.show()

        return coeffs, Rsquared