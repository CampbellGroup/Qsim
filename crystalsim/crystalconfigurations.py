import numpy as np
from objects import ion


def symmetric_6(radius):
    ions = []
    ions.append(ion(0, radius))
    ions.append(ion(0, -radius))
    x = radius * np.cos(np.pi/6)
    y = radius * np.sin(np.pi/6)
    ions.append(ion(x, y))
    ions.append(ion(-x, -y))
    ions.append(ion(-x, y))
    ions.append(ion(x, -y))
    return ions


def symmetric_4(radius):
    ions = []
    ions.append(ion(0, radius))
    ions.append(ion(radius, 0))
    ions.append(ion(0, -radius))
    ions.append(ion(-radius, 0))
    return ions


def triangle_4(radius):
    ions = []
    theta = np.pi/6.0
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    ions.append(ion(0, 0))
    ions.append(ion(0, radius))
    ions.append(ion(x, -y))
    ions.append(ion(-x, -y))
    return ions


def cross_5(radius):
    ions = []
    ions.append(ion(0, 0))
    ions.append(ion(0, radius))
    ions.append(ion(radius, 0))
    ions.append(ion(0, -radius))
    ions.append(ion(-radius, 0))
    return ions


def one_ion(radius):
    ions = []
    ions.append(ion(0, radius))
    return ions


def two_ion(radius):
    ions = []
    ions.append(ion(0, radius))
    ions.append(ion(0, -radius))
    return ions


def three_line(radius):
    ions = []
    ions.append(ion(0, radius))
    ions.append(ion(0, 0))
    ions.append(ion(0, -radius))
    return ions
