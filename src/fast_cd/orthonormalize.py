import scipy as sp
import numpy as np


def orthonormalize(B, M=None):
    if M is None:
        M = sp.sparse.identity(B.shape[0])
    # M = sp.sparse.identity(B.shape[0])

    msqrt = np.sqrt(M.diagonal())
    msqrti = 1 / msqrt
    Msqrt = sp.sparse.diags(msqrt, 0)
    Msqrti = sp.sparse.diags(msqrti, 0)
    Bm = Msqrt @ B


    [Q, R] = np.linalg.qr(Bm)

    sing = np.abs(R).sum(axis=0)
    nonsing = np.abs(R).sum(axis=1) > 1e-8  # check which rows are singular
    B3 = Msqrti @ Q[:, nonsing]

    # Bmtest = np.hstack((Bm, Bm[:, [0]]))
    # [Bm2, R] = np.linalg.qr(Bmtest)
    # nonsing = np.abs(R).sum(axis=1) > 1e-8 # check which rows are singular
    # B3 = Msqrti @ Bm2[:, nonsing]

   # C = Bm.T @ Bm
    #
    # [C, V] = np.linalg.eigs(C)
    # [U, s, V] = np.linalg.svd(C)
    # U2 = Bm @ U
    # V2 = Bm @ V
    # B2 = B @ U / s
    #
    # ii = np.where(s > 1e-9)[0]
    # B2 = U[:, ii]@V[ii, :]# @ np.diag(s[ii]) #@ V[ii, :][:, ii]
    #
    # B3 = Msqrti @ B2

    # I = B3.T @ M @ B3
    return B3
