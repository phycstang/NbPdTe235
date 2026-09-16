# Nb₂Pd₃Te₅: spurious DFPT imaginary phonon at Γ (Quantum ESPRESSO ph.x)

Diagnostic study of a **false soft mode** in Nb₂Pd₃Te₅: DFPT (`ph.x`) predicts a
large imaginary Γ-point mode (−194 to −200 cm⁻¹), while frozen-phonon
finite-displacement (`pw.x`) calculations of the same mode give a **positive**
force constant. The two methods disagree on the *sign* of K.

## Summary

| Quantity | DFPT (`ph.x`) | Finite displacement (`pw.x`) |
|---|---|---|
| Projected curvature K (eV/Å²) | **−104.89** | **+24.91** |
| Frequency (cm⁻¹) | −194.5 … −200.4 | +97.6 |

The discrepancy ΔK = −129.8 eV/Å² is **~5× larger than the entire physical
force constant**, so this is not a numerical precision issue.

Per-atom residuals r = g_DFPT − g_FD show **92.6% of the error concentrated on
Te atoms**, with Te11/12/15/16 z-components amplified by ≈2.8×. Te11/12/15/16
are the atoms moving in the layer-shearing interlayer dipole pattern
(representation 7 of the A_g block).

## System

- Nb₄Pd₆Te₁₀ unit cell (20 atoms), relaxed structure
- Pseudopotentials: ONCV PBE sr (PseudoDojo-equivalent), **Pd and Te with NLCC**, Nb without
- ecutwfc = 90 Ry, ecutrho = 360 Ry, k-grid 30×6×1
- occupations `smearing` `fd`, degauss = 0.05 eV
- `assume_isolated = '2D'` (Coulomb 2D cutoff)
- QE versions tested: 7.3.1 and 7.4.1 (both show the anomaly)

## Evidence chain

### 1. Waterfall decomposition (instrumented ph.x, exact reproduction of −104.8938)

Static terms (dynmat0, irr=0):

| Term | Contribution (eV/Å²) |
|---|---|
| dynmat_us (NL static) | +251 933.6 |
| d2ionq (Ewald) | −5 013.3 |
| dynmatcc (static NLCC) | +7 702.9 |
| **D0 total** | **+254 623.3** |

Response terms (per irrep of the A_g block, drhodvloc = ∫ ρ̄₁·dv_loc):

| irrep | drhodvloc contribution |
|---|---|
| rep 1 | −29 666.7 |
| rep 5 | −9 109.6 |
| **rep 7** | **−194 693.9** ← dominant anomaly |
| rep 8 | −6 305.7 |
| all response terms total | −259 517 |
| dynmat_nlcc total | −7 706.8 (≈ −dynmatcc, consistent) |
| drhodvnl (NC-KB) total | −11.4 (negligible) |

Net: +254 623 − 259 517 ≈ **−104.89** ✔ (exactly reproduced)

### 2. Isolated rep7 finite-displacement check

Displacing only the rep7 pattern (Te11/12/15/16 anti-phase z, amplitude
±0.005 Å, 3 SCF runs): K_FD(rep7 row) = **+46.10** eV/Å² vs
K_DFPT(rep7 row) = **−14.45** eV/Å² (diagonal). The rep7 row is independently wrong.

### 3. Excluded hypotheses

| Hypothesis | Test | Result |
|---|---|---|
| GGA XC response gradient (dgradcorr) | ph.x with dgradcorr disabled | error unchanged (Δ ≈ +595) → **excluded** |
| Fermi-energy-shift divergence (QE issue #424 mechanism) | exact recomputation of `dos_ef` (localdos.f90 formula) = 67.7 Ry⁻¹ = 2.49 states/eV; converged `def` per rep = 0.02–0.12 eV (normal) | **excluded** |
| drho magnitude anomaly | dump matrix norms: rep7 drhodvloc increment norm (124.7) same as reps 1/4/6 | error is not in \|drho\| scale |
| KB non-local response (drhodvnl) | waterfall | −11.4 eV/Å², negligible |

### 4. Remaining suspects

1. **`assume_isolated='2D'` response path** (`Coul_cut_2D_ph` Hartree kernel in
   `dv_of_drho`): rep7 is precisely the interlayer dipole pattern, the most
   sensitive case for the 2D-cutoff response. Earlier 2D on/off comparison
   (Δ = −32.8) falls entirely in the response side. Verification run in progress.
2. **Sternheimer/Hartree solve on the dipole component** (G_z = 0 sector).

## Why FD is right and DFPT wrong

FD redo the full self-consistent cycle at each displacement (occupations,
Hartree potential, 2D boundary conditions all re-converged), so the
static–response cancellation of the huge Coulomb terms (+254 623) is automatic
and exact. DFPT relies on the linear-response chain (`solve_linter` →
`dv_of_drho` → `Coul_cut_2D_ph`/`efermi_shift`); the incomplete cancellation
residual on Te z-components is −48 978 instead of ~+10.

## Related upstream issues

- [QEF #424](https://gitlab.com/QEF/q-e/-/issues/424): huge imaginary phonon in
  ZrTe₅ (also a telluride!) between QE 6.7/6.8 — diagnosed by developers as
  Fermi-energy-shift divergence for near-gap metals; but here `dos_ef` is
  healthy so the mechanism must be different.
- [QEF #457](https://gitlab.com/QEF/q-e/-/issues/457): ONCVPSP UPF pseudos,
  Γ-point DFPT wrong while psp8→Abinit correct.

## Repository contents

```
data/
  ag_qe741_result.json         A_g block result, QE 7.4.1 (K_DFPT = −104.8938)
  ag_sg15_result.json          A_g block result, earlier PP set (K_DFPT = −98.83)
  fd_T0_combined_result.json   full-mode FD reference (K_FD = +24.91)
  rep7_fd_forces.json          rep7-isolated FD forces (zero/plus/minus)
  dos_ef_analysis.md           dos_ef + def extraction (efermi_shift exclusion)
inputs/
  scf.in, ph.in                QE 7.4.1 base inputs
  rep7_fd/                     rep7-isolated FD scf inputs (zero/plus/minus)
scripts/
  analyze_partial_ag.py        A_g block reconstruction from phsave (official)
scripts/ + instrumentation notes: ph.x was patched with dump points
  (module ph_dyn_dump.f90, env var PH_DUMP_DIR); waterfall numbers above
  come from those dumps and reproduce the unpatched result bit-for-bit.
```

## Reproduction

1. `inputs/scf.in` → `pw.x` (QE 7.4.1, any ≥ ~100 cores)
2. `inputs/ph.in` → `ph.x`; the A_g block contains 10 irreps
3. Curvature of mode 1 along the mass-weighted eigenvector:
   K = −u† D u / u†u × conversions, or use `scripts/analyze_partial_ag.py`
   on the `phsave` directory.
4. FD reference: displace atoms along mode 1 (max atomic displacement = amplitude),
   3 SCF runs at 0/±0.005 Å; K_FD = (F(+u) − F(−u))·d̂ / (2×0.005).
