"""
==========================================================
Estimate the prediction intervals of 1D homoscedastic data
==========================================================

:class:`mapie.estimators.MapieRegressor` is used to estimate
the prediction intervals of 1D homoscedastic data using
different methods.
"""
from typing import Tuple

import numpy as np
import scipy
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from matplotlib import pyplot as plt

from mapie.estimators import MapieRegressor


def f(x: np.ndarray) -> np.ndarray:
    """Polynomial function used to generate one-dimensional data"""
    return np.stack(5*x + 5*x**4 - 9*x**2)


def get_homoscedastic_data(
    n_samples: int = 200,
    n_test: int = 1000,
    sigma: float = 0.1
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Generate one-dimensional data from a given function,
    number of training and test samples and a given standard
    deviation for the noise.
    The training data data is generated from an exponential distribution.

    Parameters
    ----------
    n_samples : int, optional
        Number of training samples, by default  200.
    n_test : int, optional
        Number of test samples, by default 1000.
    sigma : float, optional
        Standard deviation of noise, by default 0.1

    Returns
    -------
    Tuple[Any, Any, np.ndarray, Any, float]
        Generated training and test data.
        [0]: X_train
        [1]: y_train
        [2]: X_true
        [3]: y_true
        [4]: y_true_sigma
    """
    np.random.seed(59)
    q95 = scipy.stats.norm.ppf(0.95)
    X_train = np.random.exponential(0.4, n_samples)
    X_true = np.linspace(0.001, 1.2, n_test, endpoint=False)
    y_train = f(X_train) + np.random.normal(0, sigma, n_samples)
    y_true = f(X_true)
    y_true_sigma = q95*sigma
    return X_train, y_train, X_true, y_true, y_true_sigma


def plot_1d_data(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    y_test_sigma: float,
    y_pred: np.ndarray,
    y_pred_low: np.ndarray,
    y_pred_up: np.ndarray,
    ax: plt.Axes,
    title: str
) -> None:
    """
    Generate a figure showing the training data and estimated
    prediction intervals on test data.

    Parameters
    ----------
    X_train : np.ndarray
        Training data.
    y_train : np.ndarray
        Training labels.
    X_test : np.ndarray
        Test data.
    y_test : np.ndarray
        True function values on test data.
    y_test_sigma : float
        True standard deviation.
    y_pred : np.ndarray
        Predictions on test data.
    y_pred_low : np.ndarray
        Predicted lower bounds on test data.
    y_pred_up : np.ndarray
        Predicted upper bounds on test data.
    ax : plt.Axes
        Axis to plot.
    title : str
        Title of the figure.
    """
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim([0, 1.1])
    ax.set_ylim([0, 1])
    ax.scatter(X_train, y_train, color='red', alpha=0.3, label='training')
    ax.plot(X_test, y_test, color='gray', label='True confidence intervals')
    ax.plot(X_test, y_test - y_test_sigma, color='gray', ls='--')
    ax.plot(X_test, y_test + y_test_sigma, color='gray', ls='--')
    ax.plot(X_test, y_pred, label='Prediction intervals')
    ax.fill_between(X_test, y_pred_low, y_pred_up, alpha=0.3)
    ax.set_title(title)
    ax.legend()


X_train, y_train, X_test, y_test, y_test_sigma = get_homoscedastic_data(
    n_samples=200, n_test=200, sigma=0.1
)

polyn_model = Pipeline(
    [
        ('poly', PolynomialFeatures(degree=4)),
        ('linear', LinearRegression(fit_intercept=False))
    ]
)

methods = ['jackknife', 'jackknife_plus', 'jackknife_minmax', 'cv', 'cv_plus', 'cv_minmax']
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(3*6, 12))
axs = [ax1, ax2, ax3, ax4, ax5, ax6]
for i, method in enumerate(methods):
    mapie = MapieRegressor(
        polyn_model,
        method=method,
        alpha=0.05,
        n_splits=10,
        return_pred='ensemble'
    )
    mapie.fit(X_train.reshape(-1, 1), y_train)
    y_preds = mapie.predict(X_test.reshape(-1, 1))
    plot_1d_data(
        X_train,
        y_train,
        X_test,
        y_test,
        y_test_sigma,
        y_preds[:, 0],
        y_preds[:, 1],
        y_preds[:, 2],
        axs[i],
        method
    )
