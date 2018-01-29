import numpy as np
from .transfer import transfer
from .constants import *


def convert_line(line, to_numpy=True):
    def class_conversion(e):
        if e['CLASS'] == 'DRIFT':
            e['CLASS_CODE'] = CLASS_CODE_DRIFT
        elif e['CLASS'] == 'SBEND':
            e['CLASS_CODE'] = CLASS_CODE_SBEND
        elif e['CLASS'] == 'QUADRUPOLE':
            e['CLASS_CODE'] = CLASS_CODE_QUADRUPOLE
        else:
            e['CLASS_CODE'] = CLASS_CODE_NONE
        return e

    def apertype_conversion(e):
        if e['APERTYPE'] == 'CIRCLE':
            e['APERTYPE_CODE'] = APERTYPE_CODE_CIRCLE
        elif e['APERTYPE'] == 'RECTANGLE':
            e['APERTYPE_CODE'] = APERTYPE_CODE_RECTANGLE
        else:
            e['APERTYPE_CODE'] = APERTYPE_CODE_NONE
            e['APERTURE'] = 0.0
        return e
    line = line.apply(class_conversion, axis=1)
    line = line.apply(apertype_conversion, axis=1)
    if to_numpy:
        return line[['CLASS_CODE', 'LENGTH', 'K1', 'APERTYPE_CODE', 'APERTURE']].as_matrix()
    else:
        return line


def aperture_check(b, e):
    # Circular aperture
    if e[3] == APERTYPE_CODE_CIRCLE:
        s = (b[:, 0]**2 + b[:, 2]**2) < e[INDEX_APERTURE]**2
    # Rectangular aperture
    elif e[3] == APERTYPE_CODE_RECTANGLE:
        s = (b[:, 0]**2 < e[INDEX_APERTURE]**2) & (b[:, 2]**2 < e[INDEX_APERTURE_2]**2)
    # Unknown aperture type
    else:
        return b
    return np.compress(s, b, axis=0)


def transform_variables(line, variables):
    ll = line.reset_index()

    def transform(v):
        i = ll[ll['index'] == v[0]].index.values[0]
        j = INDEX[v[1]]
        return [i, j]
    return list(map(transform, variables))


def adjust_line(line, variables, parameters):
    for i, p in enumerate(parameters):
        line[variables[i][0], variables[i][1]] = p
    return line  # Check later if calling this function will


def track(line, b):
    r = range(0, line.shape[0])
    beams = []
    for i in r:
        matrix = transfer[int(line[i, 0])]
        if matrix is not None:
            b = b.dot(matrix(line[i]).T)
            #b = np.einsum('ij,kj->ik', b[:, 0:4], matrix)
        b = aperture_check(b, line[i])
        beams.append(b)
    return beams