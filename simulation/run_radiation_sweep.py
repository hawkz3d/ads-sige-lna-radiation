# -*- coding: utf-8 -*-
"""
SiGe HBT Cascode LNA - radiation parameter sweep (simplified model)

Sweeps the radiation degradation TREND of the thesis Ch.4
(TID / DD / EMI synergy) with a simplified small-signal BJT model,
driven by the SPICE parameter deltas of thesis Table 4-3.

Usage:
    python run_radiation_sweep.py
Output:
    radiation_sweep.png   (S21 / S11 / NF vs frequency for 3 conditions)
    radiation_summary.csv
"""
import numpy as np
import csv

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except Exception:
    HAVE_MPL = False

# --- thesis Table 4-3 parameters -------------------------------------
VT = 26e-3           # thermal voltage @ 300K
IC = 272e-6          # collector bias current (thesis 4.1.1)
RL = 50.0            # matched load
F0 = 0.7e9           # center frequency

CONDITIONS = {
    "NOM": dict(BF=272.8, RB=15.3, CJE=26.9e-15, CJC=33.4e-15, TF=0.34e-12),
    "TID": dict(BF=229.1, RB=28.9, CJE=32.1e-15, CJC=36.9e-15, TF=0.31e-12),
    "DD":  dict(BF=233.0, RB=20.3, CJE=25.3e-15, CJC=35.1e-15, TF=0.31e-12),
}

# EMI synergy: extra gain penalty + NF penalty (thesis 4.3.2)
EMI_S21_PENALTY_DB = {"NOM": 0.0, "TID": 3.2, "DD": 2.5}
EMI_NF_PENALTY_DB  = {"NOM": 0.0, "TID": 1.5, "DD": 1.4}


# output resonant tank (L_p // C_p // R_p), peaked near F0
R_P = 800.0
L_P = 40e-9
C_P = 1.0 / ((2 * np.pi * F0) ** 2 * L_P)


def sweep(freq, p):
    """Simplified cascode small-signal gain / input return loss / NF."""
    w = 2 * np.pi * freq
    gm = IC / VT
    # beta degradation -> bias current mirror re-distributes -> gm_eff drops
    gm_eff = gm * (p["BF"] / CONDITIONS["NOM"]["BF"])
    rpi = p["BF"] / gm_eff
    # Miller capacitance seen at input of the common-emitter stage
    Cm = p["CJC"] * (1 + gm_eff * R_P)
    Cin = p["CJE"] + Cm
    Zin = 1.0 / (1.0 / rpi + 1j * w * Cin + 1.0 / (p["RB"] + 1e-6))
    # input matching network: base inductor LB resonates with Cin near F0
    LB = 1.0 / ((2 * np.pi * F0) ** 2 * Cin)
    Zin_m = 1j * w * LB + Zin
    # voltage transfer from 50 ohm source into the matched network
    Tin = Zin_m / (Zin_m + RL)
    # cascode loaded gain with resonant output tank
    Z_res = 1.0 / (1.0 / R_P + 1.0 / (1j * w * L_P) + 1j * w * C_P)
    Av = gm_eff * Z_res * Tin
    S21_db = 20 * np.log10(np.abs(Av))
    # input return loss (referenced to 50 ohm)
    Gamma = (Zin_m - RL) / (Zin_m + RL)
    S11_db = 20 * np.log10(np.abs(Gamma))
    # simplified noise figure: dominated by base resistance thermal noise
    NF_db = 10 * np.log10(1 + p["RB"] / RL + 1.0 / (gm_eff * rpi))
    return S21_db, S11_db, np.full_like(S21_db, NF_db)


def main():
    freq = np.logspace(np.log10(0.2e9), np.log10(2.0e9), 200)
    print("SiGe HBT Cascode LNA - radiation trend (simplified model)")
    print("-" * 60)
    print(f"{'COND':<6} {'S21@0.7G':>9} {'S11@0.7G':>9} {'NF@0.7G':>9}")
    print("-" * 60)

    rows = []
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5)) if HAVE_MPL else (None, [])
    for name, p in CONDITIONS.items():
        S21, S11, NF = sweep(freq, p)
        idx = np.argmin(np.abs(freq - F0))
        print(f"{name:<6} {S21[idx]:9.2f} {S11[idx]:9.2f} {NF[idx]:9.2f}")
        rows.append([name, S21[idx], S11[idx], NF[idx]])
        if HAVE_MPL:
            axes[0].semilogx(freq / 1e9, S21, label=name)
            axes[1].semilogx(freq / 1e9, S11, label=name)
            axes[2].semilogx(freq / 1e9, NF, label=name)

    # EMI synergy summary (fixed at F0)
    print("\nEMI synergy at 0.7 GHz (S21 / NF after coupling EMI source)")
    print(f"{'COND':<6} {'S21_dB':>8} {'S21+EMI':>8} {'NF_dB':>7} {'NF+EMI':>7}")
    emi_rows = []
    for name in CONDITIONS:
        S21, _, NF = sweep(np.array([F0]), CONDITIONS[name])
        s21e = S21[0] - EMI_S21_PENALTY_DB[name]
        nfe = NF[0] + EMI_NF_PENALTY_DB[name]
        print(f"{name:<6} {S21[0]:8.2f} {s21e:8.2f} {NF[0]:7.2f} {nfe:7.2f}")
        emi_rows.append([name, S21[0], s21e, NF[0], nfe])

    if HAVE_MPL:
        axes[0].set_title("Gain S21 (dB)"); axes[0].set_xlabel("GHz")
        axes[1].set_title("Input return loss S11 (dB)"); axes[1].set_xlabel("GHz")
        axes[2].set_title("Noise figure NF (dB)"); axes[2].set_xlabel("GHz")
        for ax in axes:
            ax.grid(True, which="both", alpha=0.3); ax.legend()
        plt.tight_layout()
        plt.savefig("radiation_sweep.png", dpi=150)
        print("\n[fig] radiation_sweep.png saved")

    with open("radiation_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cond", "s21_db", "s11_db", "nf_db"])
        w.writerows(rows)
    print("[csv] radiation_summary.csv saved")


if __name__ == "__main__":
    main()
