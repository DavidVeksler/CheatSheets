"""Reproduce the monochromatic data; fail before writing if independent checks fail.

python scripts/rainbow/compute.py
See docs/how-do-rainbows-work-production.md for conventions and references.
"""
import json
import math
from pathlib import Path
import numpy as np
import scipy
from scipy.special import airy, gamma, spherical_jn, spherical_yn
import miepython
from iapws._iapws import _Refractive

ROOT = Path(__file__).resolve().parent


def direct_amplitudes(m, x, mu, extra=0):
    """Independent direct Riccati-Bessel series, outgoing h^(1).

    Appropriate here for moderate x and a REAL lossless index. This is a
    cross-check, not a proposed general-purpose stable Mie implementation.
    miepython uses the complex-conjugate time convention; compare intensities.
    """
    count = int(x + 4.05 * x ** .33333 + 2) + extra
    j = np.arange(1, count + 1)
    psi = x * spherical_jn(j, x)
    dpsi = spherical_jn(j, x) + x * spherical_jn(j, x, True)
    pm = m * x * spherical_jn(j, m * x)
    dpm = spherical_jn(j, m * x) + m * x * spherical_jn(j, m * x, True)
    xi = psi + 1j * x * spherical_yn(j, x)
    dxi = dpsi + 1j * (spherical_yn(j, x) + x * spherical_yn(j, x, True))
    an = (m * pm * dpsi - psi * dpm) / (m * pm * dxi - xi * dpm)
    bn = (pm * dpsi - m * psi * dpm) / (pm * dxi - m * xi * dpm)
    p0, p1 = np.zeros_like(mu), np.ones_like(mu)
    s1, s2 = np.zeros_like(mu, complex), np.zeros_like(mu, complex)
    for n, a, b in zip(j, an, bn):
        tau = n * mu * p1 - (n + 1) * p0
        c = (2 * n + 1) / (n * (n + 1))
        s1 += c * (a * p1 + b * tau)
        s2 += c * (a * tau + b * p1)
        p0, p1 = p1, ((2 * n + 1) * mu * p1 - (n + 1) * p0) / n
    return s1, s2


def stationary(m, p=2):
    i = math.asin(math.sqrt((p * p - m * m) / (p * p - 1)))
    r = math.asin(math.sin(i) / m)
    deviation = (p - 1) * math.pi + 2 * i - 2 * p * r
    theta = math.acos(math.cos(deviation))
    return dict(i=math.degrees(i), r=math.degrees(r), b=math.sin(i),
                deviation=math.degrees(deviation), theta=math.degrees(theta),
                beta=180 - math.degrees(theta))


def main():
    # Published MIEV0 case 14 intensities are printed to 6 significant digits.
    # Absolute tolerance is half of the last printed decimal place (5e-7).
    mu = np.cos(np.deg2rad([0, 30, 60, 90]))
    s1, s2 = miepython.S1_S2(1.5 - 1j, 1, mu, norm='wiscombe')
    reference = np.array([.377446, .313213, .192141, .120663])
    reference_error = np.max(np.abs((abs(s1)**2 + abs(s2)**2)/2 - reference))
    assert reference_error < 5e-7, reference_error
    # Ai(0) is independently known exactly via Gamma(2/3).
    ai0 = 1 / (3 ** (2/3) * gamma(2/3))
    assert abs(airy(0)[0] - ai0) < 1e-14
    m = 1.332
    geo = stationary(m)
    h = (9/4) * math.sqrt(4-m*m) / (m*m-1)**1.5
    beta = np.linspace(35, 43, 801)
    mu = np.cos(np.deg2rad(180-beta))
    cases, checks = {}, []
    for radius in [25, 50, 100]:
        x = 2 * math.pi * radius / .650
        s1, s2 = miepython.S1_S2(m, x, mu, norm='wiscombe')
        a1, a2 = direct_amplitudes(m, x, mu)
        b1, b2 = direct_amplitudes(m, x, mu, extra=20)
        per, par = abs(s1)**2, abs(s2)**2
        # Absolute error relative to peak avoids false blow-up at dark minima.
        # 1e-8 retains eight relative decimal places, beyond plot/data precision.
        cross = max(np.max(abs(per-abs(a1)**2))/max(per),
                    np.max(abs(par-abs(a2)**2))/max(par))
        conv = max(np.max(abs(abs(a1)**2-abs(b1)**2))/max(per),
                   np.max(abs(abs(a2)**2-abs(b2)**2))/max(par))
        # Tail check uses miepython's documented ~1e-6 series target;
        # the separate same-order independent calculation retains 1e-8.
        assert cross < 1e-8 and conv < 1e-6, (cross, conv)
        scale = h**(1/3) / x**(2/3)  # radians per unit Airy coordinate
        z = np.deg2rad(beta-geo['beta'])/scale
        ai = airy(z)[0]**2
        s = miepython.S1_S2(m, x, np.array([math.cos(math.radians(140))]), norm='wiscombe')
        cases[str(radius)] = dict(x=x, scale_degrees=math.degrees(scale),
            perpendicular=[round(float(v), 8) for v in per],
            parallel=[round(float(v), 8) for v in par],
            airy=[round(float(v), 10) for v in ai],
            at_theta140=dict(perpendicular=float(abs(s[0][0])**2), parallel=float(abs(s[1][0])**2)))
        checks.append(dict(radius_um=radius, independent_peak_relative_error=float(cross),
                           extra20_peak_relative_error=float(conv)))
    result = dict(wavelength_um=.650, relative_index=m, beta_start=35,
        beta_step=.01, count=801, geometry=geo, h=h,
        ray_presets=[dict(nm=int(w*1000), n=_Refractive(998.2,293.15,w)) for w in [.65,.55,.45]],
        ideal_primary=stationary(4/3), ideal_secondary=stationary(4/3,3), cases=cases)
    (ROOT/'data.json').write_text(json.dumps(result, separators=(',',':'))+'\n', encoding='utf-8')
    report = dict(versions=dict(numpy=np.__version__,scipy=scipy.__version__,miepython=miepython.__version__),
                  miev0_max_absolute_error=float(reference_error), airy0=float(ai0), checks=checks)
    (ROOT/'numerical-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(validation=report,primary=result['ideal_primary'],secondary=result['ideal_secondary'],
                         example=cases['100']['at_theta140'],h=h,scale=cases['100']['scale_degrees']),indent=2))


if __name__ == '__main__':
    main()
