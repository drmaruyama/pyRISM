#!/usr/bin/env python3

import numpy as np
from scipy.spatial.transform import Rotation as R

def total_moment(dat):
    total_mom = []
    dm_vecs = []
    for isp in dat.species:
        total_charge = 0.0
        centre_of_charge = np.zeros(3, dtype=np.float64)
        dipole_mom_vec = np.zeros(3, dtype=np.float64)

        for iat in isp.atom_sites:
            total_charge += np.abs(iat.params[-1])

        if total_charge == 0:
            continue

        for iat in isp.atom_sites:
            centre_of_charge += np.abs(iat.params[-1]) * iat.coords
        centre_of_charge /= total_charge

        for iat in isp.atom_sites:
            iat.coords -= centre_of_charge

        for iat in isp.atom_sites:
            dipole_mom_vec += iat.params[-1] * iat.coords

        dipole_mom = np.sqrt(np.sum(dipole_mom_vec * dipole_mom_vec))

        if dipole_mom < 1E-16:
            continue

        total_mom.append(dipole_mom)
        dm_vecs.append(dipole_mom_vec)

    return (np.asarray(total_mom).sum(), dm_vecs)

def dipole_moment(isp):
    total_charge = 0.0
    centre_of_charge = np.zeros(3, dtype=np.float64)
    dipole_mom_vec = np.zeros(3, dtype=np.float64)

    for iat in isp.atom_sites:
        total_charge += np.abs(iat.params[-1])

    if total_charge == 0:
        return (0.0, np.asarray([0.0, 0.0, 0.0]))

    for iat in isp.atom_sites:
        centre_of_charge += np.abs(iat.params[-1]) * iat.coords
    centre_of_charge /= total_charge

    for iat in isp.atom_sites:
        iat.coords -= centre_of_charge

    for iat in isp.atom_sites:
        dipole_mom_vec += iat.params[-1] * iat.coords

    dipole_mom = np.sqrt(np.sum(dipole_mom_vec * dipole_mom_vec))

    if dipole_mom < 1E-16:
        return (0.0, np.asarray([0.0, 0.0, 0.0]))

    return dipole_mom, dipole_mom_vec


def quaternion_from_Euler_axis(angle, direction):
    quat = np.zeros(4, dtype=np.float64)

    magn = np.sqrt(np.sum(direction * direction))
    quat[3] = np.cos(angle / 2.0)
    if magn == 0:
        quat[0:3] = 0
    else:
        quat[0:3] = direction / magn * np.sin(angle / 2.0)
    return quat

def align_dipole(dat):
    zaxis = np.asarray([0.0, 0.0, 1.0])
    yaxis = np.asarray([0.0, 1.0, 0.0])

    for isp in dat.species:
        dm, dmvec = dipole_moment(isp)
        if not dmvec.any():
            continue
        angle = -np.arccos(dmvec[0] / np.sqrt(np.sum(dmvec * dmvec)))
        quat = quaternion_from_Euler_axis(angle, np.copysign(zaxis, dmvec[1]))
        rotation_around_z = R.from_quat(quat)
        new_dmvec = np.zeros_like(dmvec)
        for iat in isp.atom_sites:
            iat.coords = rotation_around_z.apply(iat.coords)

        for iat in isp.atom_sites:
            new_dmvec += iat.params[-1] * iat.coords

        angle_2 = -np.arccos(new_dmvec[2] / np.sqrt(np.sum(new_dmvec * new_dmvec)))
        quat_2 = quaternion_from_Euler_axis(angle_2, yaxis)
        final_dmvec = np.zeros_like(dmvec)
        rotation_around_y = R.from_quat(quat_2)
        for iat in isp.atom_sites:
            iat.coords = rotation_around_y.apply(iat.coords)

        for iat in isp.atom_sites:
            final_dmvec += iat.params[-1] * iat.coords

def check_symmetric(a, rtol=1e-05, atol=1e-08):
    return np.allclose(a, a.T, rtol=rtol, atol=atol)

def j0(x):
    return np.sin(x) / x

def j1(x):
    return ((np.sin(x) / x) - np.cos(x)) / x
