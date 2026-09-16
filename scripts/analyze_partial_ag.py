#!/usr/bin/env python3
"""Diagonalize the complete Ag block from partial QE Gamma-phonon restarts."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DEFAULT_PHSAVE = HERE / "tmp" / "_ph0" / "NbPdTe235_sg15.phsave"
REFERENCE_METADATA = HERE.parent / "04_pp_mode_test_20260829" / "metadata.json"

NAT = 20
NMODE = 3 * NAT
N_AG = 10
RY_EV = 13.605693122994
BOHR_ANG = 0.529177210903
EV_A2_TO_N_M = 16.02176634
AMU_KG = 1.66053906660e-27
C_CM_S = 2.99792458e10
FLOAT_RE = re.compile(r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][+-]?\d+)?")


def numbers(text: str) -> list[float]:
    return [float(item.replace("D", "E").replace("d", "e")) for item in FLOAT_RE.findall(text)]


def complex_values(text: str) -> np.ndarray:
    values = np.asarray(numbers(text), dtype=float)
    if values.size % 2:
        raise ValueError("Odd number of real/imaginary values")
    return values[0::2] + 1j * values[1::2]


def read_patterns(path: Path) -> np.ndarray:
    root = ET.parse(path).getroot()
    vectors = []
    for element in root.iter("DISPLACEMENT_PATTERN"):
        vector = complex_values(element.text or "")
        if vector.size != NMODE:
            raise ValueError(f"Expected {NMODE} entries in a pattern, found {vector.size}")
        vectors.append(vector)
    if len(vectors) != NMODE:
        raise ValueError(f"Expected {NMODE} patterns, found {len(vectors)}")
    return np.column_stack(vectors)


def read_partial(path: Path) -> np.ndarray:
    root = ET.parse(path).getroot()
    done = root.findtext(".//DONE_IRR")
    if done is None or done.strip().lower() != "true":
        raise ValueError(f"Incomplete partial matrix: {path}")
    element = root.find(".//PARTIAL_DYN")
    if element is None:
        raise ValueError(f"No PARTIAL_DYN in {path}")
    values = complex_values(element.text or "")
    if values.size != NMODE * NMODE:
        raise ValueError(f"Expected {NMODE * NMODE} entries in {path}, found {values.size}")
    return values.reshape((NMODE, NMODE), order="F")


def signed_frequency(eigenvalue_s2: float) -> float:
    sign = -1.0 if eigenvalue_s2 < 0.0 else 1.0
    return sign * np.sqrt(abs(eigenvalue_s2)) / (2.0 * np.pi * C_CM_S)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phsave", type=Path, default=DEFAULT_PHSAVE)
    parser.add_argument("--output", type=Path, default=HERE / "ag_partial_result.json")
    args = parser.parse_args()
    phsave = args.phsave.resolve()

    metadata = json.loads(REFERENCE_METADATA.read_text())
    atoms = metadata["atoms"]
    masses_by_species = {"Nb": 92.90638, "Pd": 106.42, "Te": 127.6}
    cartesian_masses = np.repeat(
        np.asarray([masses_by_species[atom["species"]] for atom in atoms]), 3
    )
    reference_direction = np.asarray(
        [row["direction"] for row in metadata["mapping"]], dtype=float
    ).reshape(NMODE)

    patterns = read_patterns(phsave / "patterns.1.xml")
    orthogonality_error = np.max(np.abs(patterns.conj().T @ patterns - np.eye(NMODE)))
    ag_patterns = patterns[:, :N_AG]
    mass_ag_amu = ag_patterns.conj().T @ (cartesian_masses[:, None] * ag_patterns)

    partials = [read_partial(phsave / f"dynmat.1.{index}.xml") for index in range(N_AG + 1)]
    force_ag_ry_bohr2 = np.sum(partials, axis=0)[:N_AG, :N_AG]
    hermiticity_error = np.max(np.abs(force_ag_ry_bohr2 - force_ag_ry_bohr2.conj().T))
    force_ag_ry_bohr2 = 0.5 * (force_ag_ry_bohr2 + force_ag_ry_bohr2.conj().T)

    mass_values, mass_vectors = np.linalg.eigh(mass_ag_amu * AMU_KG)
    if np.min(mass_values) <= 0.0:
        raise ValueError("Ag mass matrix is not positive definite")
    inverse_mass_half = (
        mass_vectors * (1.0 / np.sqrt(mass_values))[None, :]
    ) @ mass_vectors.conj().T

    force_ag_n_m = force_ag_ry_bohr2 * (RY_EV / BOHR_ANG**2) * EV_A2_TO_N_M
    dynamical_ag_s2 = inverse_mass_half @ force_ag_n_m @ inverse_mass_half
    eigenvalues_s2, _ = np.linalg.eigh(dynamical_ag_s2)
    frequencies_cm1 = [float(signed_frequency(value)) for value in eigenvalues_s2]

    coefficients = patterns.conj().T @ reference_direction
    outside_ag_norm = float(np.linalg.norm(coefficients[N_AG:]))
    reference_coefficients = coefficients[:N_AG]
    projected_ry_bohr2 = np.vdot(
        reference_coefficients, force_ag_ry_bohr2 @ reference_coefficients
    )
    if abs(projected_ry_bohr2.imag) > 1.0e-7:
        raise ValueError(f"Projected curvature is complex: {projected_ry_bohr2}")
    projected_ev_a2 = float(projected_ry_bohr2.real * RY_EV / BOHR_ANG**2)
    effective_mass_amu = float(np.dot(cartesian_masses, reference_direction**2))
    projected_eigenvalue_s2 = (
        projected_ev_a2 * EV_A2_TO_N_M / (effective_mass_amu * AMU_KG)
    )
    projected_frequency_cm1 = float(signed_frequency(projected_eigenvalue_s2))

    result = {
        "phsave": str(phsave),
        "number_of_ag_patterns": N_AG,
        "pattern_orthogonality_max_error": float(orthogonality_error),
        "ag_hermiticity_max_error_ry_per_bohr2": float(hermiticity_error),
        "reference_mode_outside_ag_coefficient_norm": outside_ag_norm,
        "ag_frequencies_cm-1": frequencies_cm1,
        "reference_mode_projected_curvature_ev_per_angstrom2": projected_ev_a2,
        "reference_mode_effective_mass_amu": effective_mass_amu,
        "reference_mode_projected_frequency_cm-1": projected_frequency_cm1,
    }
    args.output.resolve().write_text(json.dumps(result, indent=2) + "\n")

    print(f"Pattern orthogonality max error: {orthogonality_error:.3e}")
    print(f"Ag Hermiticity max error: {hermiticity_error:.3e} Ry/bohr^2")
    print(f"Reference mode outside-Ag norm: {outside_ag_norm:.3e}")
    print("Ag frequencies (cm^-1):")
    print("  " + " ".join(f"{value:+.6f}" for value in frequencies_cm1))
    print(f"Reference projected curvature: {projected_ev_a2:+.6f} eV/A^2")
    print(f"Reference projected frequency: {projected_frequency_cm1:+.6f} cm^-1")


if __name__ == "__main__":
    main()
