# 2D cutoff exclusion — no-2D rep7 verification

Date: 2026-09-17. Purpose: test whether the `assume_isolated='2D'` Coulomb
cutoff response path (`Coul_cut_2D_ph`) is the source of the rep7 anomaly.

## Setup

- Same base system (QE 7.4.1, dump-instrumented ph.x, 30×6×1 k-grid)
- New SCF without `assume_isolated='2D'` (no2d; converged E = −4221.98258400 Ry)
- ph.x run for rep7 only (`start_irr = last_irr = 7`), npool 8, 4 nodes, 55 min
- rep7 = pattern index 6 (of the A_g block, patterns 0–9): u7 support only on
  Te11/12/15/16 (1-based), anti-phase z, max|u7| = 0.450 — interlayer dipole

## Result (pattern-basis diagonal, eV/Å²)

| Boundary condition | Static D0 diag[6,6] | Response | Cumulative K(rep7) |
|---|---|---|---|
| 2D cutoff | +50 411.20 | −50 716.22 | −50 305.02 |
| no 2D cutoff | ≈ +50 411 (assumed ≈ same) | −100 829.15 | **−50 417.95** |
| FD reference (2D boundary) | — | — | **+46.10** |

Key numbers from `dynmat.1.7.xml` (cumulative = D0 + responses so far):

- 2D run: cum diag[6,6] = −50 305.02
- no2D run: cum diag[6,6] = −50 417.95

**2D vs no2D differ by only −112.93 eV/Å², while the error is ~−50 000 eV/Å².
The anomaly persists without the 2D cutoff → `Coul_cut_2D_ph` is NOT the main
error source.**

## Updated hypothesis status

| Hypothesis | Status |
|---|---|
| GGA XC response (dgradcorr) | ❌ excluded (noGGA: Δ ≈ +595) |
| Fermi-energy-shift divergence (#424) | ❌ excluded (dos_ef = 2.49 states/eV healthy) |
| 2D cutoff (Coul_cut_2D_ph) | ❌ excluded (Δ = −113 vs error −50 000) |
| drho magnitude anomaly | ❌ excluded (dump norms comparable across reps) |
| KB non-local response | ❌ negligible (−11.4) |
| NLCC static–response | ✅ self-consistent cancellation normal |
| **dv_of_drho / Hartree solve of dvscf (long-range screening)** | **primary suspect** |
| Sternheimer solve itself | secondary (thresh history looks clean) |

## no2D FD reference (completed)

With identical displacement inputs and the same d7 convention (pattern index 6,
max|u|=1):

| Method | 2D boundary | no 2D boundary |
|---|---|---|
| FD | −46.10 eV/Å² | −46.10 eV/Å² |
| DFPT (cumulative diag[6,6], QE pattern basis) | −50 305.02 | −50 417.95 |

- FD is boundary-independent (−46.10 both) ✔ as expected
- DFPT changes by only −112.93 between boundaries — the anomaly (−50 000) is
  entirely independent of the 2D cutoff
- Note: the earlier reported FD +46.10 used the opposite d7 sign; magnitudes agree
- (See data/rep7_no2d_result.json)

## Remaining work

- Grid-point comparison of rep7 converged dvscfin vs FD SCF potential difference
- The anomaly is in the DFPT response chain itself (dv_of_drho / Hartree screening
  or the Sternheimer solution), specific to the interlayer dipole pattern
