import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def normalize_plate(plate, tip, err_rand, err_sys, runs=1, C_target=1.0, V_transfer=100.0):
    """Round-1 OD of every well after transfer + dilution.

    Each run draws one pipette bias ~ Uniform(-err_sys, err_sys), shared by every dispense on the
    plate; each dispense gets its own random error ~ Normal(0, err_rand). Returns C_final, the true
    culture volume V_t in the well after transfer and the true media volume V_d added in the
    dilution (uL), each shape (runs, *plate.shape).
    """
    b = np.random.uniform(-err_sys, err_sys, (runs, 1))
    C_final, V_t, V_d = np.zeros((3, runs) + plate.shape)
    for idx, c0 in np.ndenumerate(plate):
        vd = V_transfer * (c0 / C_target - 1)  # nominal media dose (uL)
        pt = np.array([tip] * int(V_transfer // tip) + ([V_transfer % tip] if V_transfer % tip > 1e-9 else []))
        pd = np.array([tip] * int(vd // tip) + ([vd % tip] if vd % tip > 1e-9 else []))
        vt_true = (pt * (1 + b + np.random.normal(0, err_rand, (runs, len(pt))))).sum(axis=1)  # true culture volume
        vd_true = (pd * (1 + b + np.random.normal(0, err_rand, (runs, len(pd))))).sum(axis=1)  # true media volume
        C_final[(slice(None),) + idx] = c0 * vt_true / (vt_true + vd_true)
        V_t[(slice(None),) + idx], V_d[(slice(None),) + idx] = vt_true, vd_true
    return C_final, V_t, V_d


def plot_od_flow(plate, C_final, title="", save=None):
    """OD after transfer (top) and after round-1 dilution (bottom), on one colour scale.

    If save is a file path, the figure is also written there.
    """
    fig, ax = plt.subplots(2, 1, figsize=(14, 10))
    od_lim = (min(plate.min(), C_final.min()), max(plate.max(), C_final.max()))
    sns.heatmap(plate, annot=True, fmt=".2f", annot_kws={"size": 7}, cmap="viridis", vmin=od_lim[0], vmax=od_lim[1],
                ax=ax[0], cbar_kws={"label": "OD"})
    sns.heatmap(C_final, annot=True, fmt=".3f", annot_kws={"size": 7}, cmap="viridis", vmin=od_lim[0], vmax=od_lim[1],
                ax=ax[1], cbar_kws={"label": "OD"})
    ax[0].set_title("OD after transfer")
    ax[1].set_title("OD after round-1 dilution")
    fig.suptitle(title)
    plt.tight_layout()
    if save:
        fig.savefig(save, dpi=200, bbox_inches="tight")
    plt.show()


def plot_volume_flow(V_t, V_d, V_transfer=100.0, title="", save=None):
    """Volume in well after transfer (top, centred on the nominal transfer) and after round-1 dilution (bottom).

    If save is a file path, the figure is also written there.
    """
    fig, ax = plt.subplots(2, 1, figsize=(14, 10))
    dv = np.abs(V_t - V_transfer).max()  # largest transfer over/undershoot (uL)
    sns.heatmap(V_t, annot=True, fmt=".1f", annot_kws={"size": 7}, cmap="bwr", center=V_transfer,
                vmin=V_transfer - dv, vmax=V_transfer + dv, ax=ax[0], cbar_kws={"label": "volume (uL)"})
    sns.heatmap(V_t + V_d, annot=True, fmt=".1f", annot_kws={"size": 7}, cmap="Blues",
                ax=ax[1], cbar_kws={"label": "volume (uL)"})
    ax[0].set_title("Volume in well after transfer (uL)")
    ax[1].set_title("Volume in well after round-1 dilution (uL)")
    fig.suptitle(title)
    plt.tight_layout()
    if save:
        fig.savefig(save, dpi=200, bbox_inches="tight")
    plt.show()
