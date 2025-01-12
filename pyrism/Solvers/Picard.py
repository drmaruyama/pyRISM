#!/usr/bin/env python3

from pyrism.Core import RISM_Obj
import numpy as np
from dataclasses import dataclass, field
from .Solver_object import *
from numba import njit
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings
import sys

np.set_printoptions(edgeitems=30, linewidth=180,
    formatter=dict(float=lambda x: "%.5g" % x))

@dataclass
class Picard(SolverObject):

    def solve(self, RISM, Closure, lam, verbose=False):
        i: int = 0
        
        if verbose == True:
            print("\nSolving solvent-solvent RISM equation...\n")
        while i < self.max_iter:

            c_prev = self.data_vv.c
            try:
                RISM()
                c_A = Closure(self.data_vv)
            except FloatingPointError as e:
                print(e)
                print("Possible divergence")
                print("iteration: {i}".format(i=i))
                print("diff: {diff}".format(diff=(c_A-c_prev).sum()))

            c_next = self.step_Picard(c_A, c_prev)

            self.data_vv.c = c_next

            if self.converged(c_next, c_prev) and verbose == True:
                self.epilogue(i, lam)
                break
            elif self.converged(c_next, c_prev):
                break

            i += 1

            if i == self.max_iter and verbose == True:
                print("Max iteration reached!")
                self.epilogue(i, lam)
                break
            elif i == self.max_iter:
                break

    def solve_uv(self, RISM, Closure, lam, verbose=False):
        i: int = 0
        if verbose == True:
            print("\nSolving solute-solvent RISM equation...\n")
        while i < self.max_iter:

            c_prev = self.data_uv.c
            try:
                RISM()
                c_A = Closure(self.data_uv)
            except FloatingPointError as e:
                print(e)
                print("Possible divergence")
                print("iteration: {i}".format(i=i))
                print("diff: {diff}".format(diff=(c_A-c_prev).sum()))

            c_next = self.step_Picard(c_A, c_prev)

            self.data_uv.c = c_next

            if self.converged(c_next, c_prev) and verbose == True:
                self.epilogue(i, lam)
                break
            elif self.converged(c_next, c_prev):
                break

            i += 1

            if i == self.max_iter and verbose == True:
                print("Max iteration reached!")
                self.epilogue(i, lam)
                break
            elif i == self.max_iter:
                break
