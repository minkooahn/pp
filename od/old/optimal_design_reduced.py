from __future__ import division

import sys
import numpy as np
from math import pi
from scipy import optimize, linalg

import response_surface_reduced as rs
import information_matrix_reduced as im



def estimate_theta(yobs, tau, phi, omega, theta):
    # hard code parameter limits:
    N = omega.size
    llim = np.zeros(3*N)
    ulim = np.ones(3*N) * np.inf
    llim[0:N] = 0. # amplitude
    llim[N:2*N] = 1. # lambda
    llim[2*N:3*N] = .5 # S2tc

    try:
        # least squares fit of response surface to data
        resid = lambda theta: (rs.y(tau,phi,theta,omega) - yobs).ravel()
        #out = optimize.leastsq(resid, theta, full_output=1)
        out = optimize.least_squares(resid, theta, bounds=(llim,ulim))
        theta_hat = out.x

        # calculate uncertainties
        # https://mail.scipy.org/pipermail/scipy-user/2013-March/034316.html
        reduced_chi_square = (resid(theta_hat)**2).sum() / (yobs.size - theta_hat.size)
        hess = np.dot(out.jac.T,out.jac)
        jac = np.linalg.inv(hess)
        pcov = jac * reduced_chi_square
        sigma = np.sqrt(pcov.diagonal())
        # normalise covariance matrix: cov_ij -> cov_ij / SE_i SE_j
        # http://graphpad.com/support/faq/how-does-prism-compute-the-normalized-covariance-matrix-how-does-it-relate-to-the-actual-covariance-matrix/
        
        pcov = pcov / sigma.reshape(1,-1)
        pcov = pcov / sigma.reshape(-1,1)
    except:
        print
        print "----------------"
        print "SINGULAR MATRIX!"
        print "----------------"
        print
        print "Theta_hat will not be updated."
        sigma = np.zeros_like(theta)
        theta_hat = theta
        pcov = []

    return (theta_hat, sigma, pcov)


def estimate_theta_and_omega(yobs, tau, phi, theta0):
    # theta0 = [N*amplitude N*lambda N*S2tc N*omega]
    
    # hard code parameter limits:
    N = theta0.size // 4
    llim = np.zeros(4*N)
    ulim = np.ones(4*N) * np.inf
    llim[0:N] = 0. # amplitude
    llim[N:2*N] = 1. # lambda
    llim[2*N:3*N] = .5 # S2tc
    llim[3*N:4*N] = -1000 # omega
    ulim[3*N:4*N] = 1000 # omega

    try:
        # least squares fit of response surface to data
        resid = lambda theta: (rs.y(tau,phi,theta[0:3*N],theta[3*N:4*N]) - yobs).ravel()
        print resid(theta0)
        #out = optimize.leastsq(resid, theta, full_output=1)
        out = optimize.least_squares(resid, theta0, bounds=(llim,ulim))
        theta_hat = out.x

        # calculate uncertainties
        # https://mail.scipy.org/pipermail/scipy-user/2013-March/034316.html
        reduced_chi_square = (resid(theta_hat)**2).sum() / (yobs.size - theta_hat.size)
        hess = np.dot(out.jac.T,out.jac)
        jac = np.linalg.inv(hess)
        pcov = jac * reduced_chi_square
        sigma = np.sqrt(pcov.diagonal())
        # normalise covariance matrix: cov_ij -> cov_ij / SE_i SE_j
        # http://graphpad.com/support/faq/how-does-prism-compute-the-normalized-covariance-matrix-how-does-it-relate-to-the-actual-covariance-matrix/
        
        pcov = pcov / sigma.reshape(1,-1)
        pcov = pcov / sigma.reshape(-1,1)
    except:
        print
        print "----------------"
        print "SINGULAR MATRIX!"
        print "----------------"
        print
        print "Theta_hat will not be updated."
        sigma = np.zeros_like(theta0)
        theta_hat = theta0
        pcov = []

    return (theta_hat, sigma, pcov)




def direct_search_next_tau(yobs, tau, phi, omega, theta_hat, tau_min=20e-6, tau_max=0.1):
    # find best-fit point by direct search (fixed phi = 0)

    # find optimal point x(N+1) (point of maximum dispersion)
    # by direct search over possible sampling times, t:
    t = np.arange(tau_min,tau_max,.0001)
    m = np.zeros_like(t)
    for i in range(t.size):
        t_control = t[i];
        phi_control = np.array(0.);
        F = rs.jac(t_control, phi_control, theta_hat, omega)
        m[i] = np.trace(np.dot(F.T, \
                               linalg.solve(im.Mdiscrete(tau,phi,theta_hat,omega), F)))

    # find point of maximum dispersion, i.e. optimal point for next observation
    i = np.argmax(m)
    tau_new = t[i]

    return tau_new


def direct_search_next_point(yobs, tau, phi, omega, theta_hat, tau_min=20e-6, tau_max=0.1):
    # find best-fit point by direct search of tau and phi

    # find optimal point x(N+1) (point of maximum dispersion)
    # by direct search over possible sampling times, t:
    #t = np.logspace(np.log10(tau_min),np.log10(tau_max),num=50)
    t = np.arange(tau_min,tau_max,.0001)
    p = np.linspace(0.,np.pi,num=4,endpoint=False)

    m = np.zeros((t.size,p.size))
    def M(t_control, phi_control):
        #t_control = x[0]
        #phi_control = x[1]
        F = rs.jac(t_control, phi_control, theta_hat, omega)
        return -1 * np.trace(np.dot(F.T, \
            linalg.solve(im.Mdiscrete(tau,phi,theta_hat,omega), F)))

    #rranges = (slice(tau_min, tau_max, 0.001), slice(0, 0.75*np.pi, 0.25*np.pi))
    #result = optimize.brute(M, rranges, finish=None)
    #result = optimize.minimize(M, result, bounds=[(20e-6,0.1),(0,np.pi)])
    #tau_new = result.x[0]
    #phi_new = result.x[1]

    for i in xrange(t.size):
        for j in xrange(p.size):
            t_control = t[i];
            phi_control = p[j];
            m[i,j] = -1*M(t_control, phi_control)
            #F = response_surface.jac(t_control, phi_control, theta_hat, omega)
            # m[i,j] = np.trace(np.dot(F.T, \
            #                    linalg.solve(information_matrix.Mdiscrete(tau,phi,theta_hat,omega), F)))
    
    # find point of maximum dispersion, i.e. optimal point for next observation
    index = np.unravel_index(m.argmax(), m.shape)
    tau_new = t[index[0]]
    phi_new = p[index[1]]

    return (tau_new, phi_new)
