# dos_ef and def analysis — exclusion of the Fermi-energy-shift divergence hypothesis

Date: 2026-09-16. Purpose: test whether the QE issue #424 mechanism
(Fermi-energy-shift divergence for near-gap metals) explains the Nb₂Pd₃Te₅
DFPT anomaly.

## 1. dos_ef exactly as computed by localdos.f90

Formula (LR_Modules/localdos.f90, ngauss = −99 Fermi–Dirac):

    dos_ef = Σ_k weight_k Σ_b w0gauss((ε_kb − ε_F)/degauss)/degauss

with degauss = 0.05 eV, ε_F = −4.6134 eV, k-grid 30×6×1 (64 irreducible k-points),
200 bands, from data-file-schema.xml of the base SCF run.

**Result: dos_ef = 67.71 Ry⁻¹ = 2.49 states/eV (both spins) = 1.24 states/eV/spin.**

This is a healthy metallic DOS magnitude, orders of magnitude away from the
near-zero DOS(E_F) that causes divergence in `ef_shift` (`def = −Δn/dos_ef`).
N(E) is monotonic around E_F (N(E_F±0.05 eV) = 320.00 ± 0.23, exact target 320),
unlike the pathological non-monotonic N(E) of issue #424.

## 2. Fermi energy shift `def` actually used by ph.x (from phdump_ph.out)

ph.x prints `Pert. #  n: Fermi energy shift (Ry) = ...` at every Sternheimer
iteration (from LR_Modules/efermi_shift.f90 line 105). Converged values per
representation:

| rep | def (Ry) | def (eV) |
|---|---|---|
| 1 | −1.1852e-03 | −0.0161 |
| 2 | +2.9294e-03 | +0.0399 |
| 3 | −7.4247e-03 | −0.1010 |
| 4 | −7.6610e-03 | −0.1042 |
| 5 | −1.8461e-03 | −0.0251 |
| 6 | −5.4845e-03 | −0.0746 |
| 7 | −8.9326e-03 | −0.1215 |
| 8 | −3.6767e-03 | −0.0500 |
| 9 | −1.3365e-03 | −0.0182 |
| 10 | −3.7285e-03 | −0.0507 |

- Imaginary parts ~1e−28 Ry (numerical zero) — the solve is clean.
- rep7 has the largest |def| (0.12 eV) but this is a **uniform Fermi-surface
  renormalization** applied as `drhoscf += def·ldos`; a shift of ~0.1 eV cannot
  produce a −194 694 eV/Å² single-term anomaly (that would require def ~ 10⁴ eV).

## 3. drhodvloc increment norms per rep (from dump matrices)

| rep | \|wdyn_before\| | \|wdyn_after\| | \|increment\| |
|---|---|---|---|
| 1 | 8.832e+02 | 1.009e+03 | 1.265e+02 |
| 4 | 8.837e+02 | 1.006e+03 | 1.235e+02 |
| 6 | 8.836e+02 | 1.008e+03 | 1.252e+02 |
| **7** | **8.830e+02** | **1.007e+03** | **1.247e+02** |

rep7's response-density increment norm is the same as other reps — the anomaly
is not in |drho| itself but in the projection of the response onto the rep7
dipole mode direction.

## Conclusion

The Fermi-energy-shift divergence mechanism (issue #424) is **excluded**:
dos_ef is healthy, def is small and clean. Attention remains on the
`assume_isolated='2D'` response path (Coul_cut_2D_ph) — rep7 is the interlayer
dipole pattern, the most sensitive case for the 2D Coulomb cutoff response.
