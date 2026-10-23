"""Graphic for Part 1.1: the 5-dispense source-to-destination transfer and how its error compounds.

Run from anywhere (no project environment needed):

    uv run --with matplotlib --with numpy python Part1/figures/make_dispense_split_figure.py

Writes dispense_split_error.png (and .svg) next to this script.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Patch, Polygon, Rectangle

OUT_DIR = Path(__file__).resolve().parent

# --- Process parameters (Part 1.1: Opentrons Flex 1-ch, 20 uL tip, 1 uL row) ---
V_WELL_UL = 200.0  # starting volume of each well
V_TIP_UL = 20.0  # tip capacity = volume per dispense
CV_RANDOM = 0.035  # random error, % CV (per dispense)
BIAS_SYS = 0.08  # systematic error bound, +/- % D (per dispense)

V_DEST_UL = V_WELL_UL / 2  # half of the well is moved to the destination plate
N_DISP = int(round(V_DEST_UL / V_TIP_UL))  # = 5
assert N_DISP == 5

k = np.arange(1, N_DISP + 1)
v_nominal = V_TIP_UL * k  # cumulative volume in the destination well
# Systematic error is one pipette's bias, so it is the same in every dispense
# (fully correlated) and adds linearly.
err_sys = BIAS_SYS * V_TIP_UL * k
# Random errors are independent per dispense and add in quadrature.
err_rand = CV_RANDOM * V_TIP_UL * np.sqrt(k)

# --- Style (dataviz reference palette, light mode; blue/orange pass the validator) ---
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e6e5e1"
C_RAND = "#2a78d6"  # categorical slot 1
C_SYS = "#eb6834"  # categorical slot 2
C_WELL = "#c9c8c2"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 10,
        "text.color": INK,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK2,
        "xtick.color": INK2,
        "ytick.color": INK2,
    }
)



C_LIQ = "#cfe0f7"  # culture liquid held in the tip
C_BODY = "#a9a8a1"  # pipette body


def pipette(cx, y_bottom, tip_h=22, body_h=12):
    """Pipette tip (filled to its 20 uL limit) with a short body on top; y in data units."""
    top = y_bottom + tip_h
    ax.add_patch(Polygon([(cx - 0.03, y_bottom), (cx + 0.03, y_bottom), (cx + 0.12, top), (cx - 0.12, top)],
                         closed=True, fc=C_LIQ, ec=INK2, lw=1.3, zorder=8))
    ax.add_patch(Rectangle((cx - 0.14, top), 0.28, body_h, fc=C_BODY, ec=INK2, lw=1.3, zorder=8))


fig, ax = plt.subplots(figsize=(12, 5.9), facecolor=SURFACE)
fig.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.15)
ax.set_facecolor(SURFACE)
XMIN, XMAX = -1.0, 5.6
ax.set_xlim(XMIN, XMAX)
ax.set_ylim(0, 158)
for s in ("top", "right", "bottom"):
    ax.spines[s].set_visible(False)
AXIS_X = 0.45  # y-axis sits between the source well and the destination wells
ax.spines["left"].set_position(("data", AXIS_X))
ax.spines["left"].set_bounds(0, 100)
ax.set_xticks([])
ax.set_yticks([0, 50, 100])
ax.text(AXIS_X - 0.25, 50, "Destination-well volume (µL)", rotation=90, ha="center", va="center", color=INK2)

W = 0.5  # well width in x units
for i, kk in enumerate(k):
    # well outline (0..100 uL = the 100 uL target) and nominal fill
    ax.add_patch(Rectangle((kk - W / 2, 0), W, V_DEST_UL, fill=False, ec=INK2, lw=1.4, zorder=3))
    ax.add_patch(Rectangle((kk - W / 2, 0), W, v_nominal[i] - V_TIP_UL, fc=C_WELL, ec="none", alpha=0.55, zorder=1))
    # the layer added by this dispense
    ax.add_patch(Rectangle((kk - W / 2, v_nominal[i] - V_TIP_UL), W, V_TIP_UL, fc=C_WELL, ec="none", zorder=1))
    # error bands around the fill level: systematic bound (wide, light) and random +/-1 sigma (inside)
    ax.add_patch(Rectangle((kk - W / 2 - 0.06, v_nominal[i] - err_sys[i]), W + 0.12, 2 * err_sys[i],
                           fc=C_SYS, ec="none", alpha=0.35, zorder=4))
    ax.add_patch(Rectangle((kk - W / 2 - 0.06, v_nominal[i] - err_rand[i]), W + 0.12, 2 * err_rand[i],
                           fc=C_RAND, ec="none", zorder=6))

    # pipette dispensing its 20 uL
    ax.text(kk, 151, f"Dispense {kk}", ha="center", va="center", fontsize=10.5, fontweight="bold")
    pipette(kk, 111)
    ax.text(kk + 0.2, 122, "+20 µL", ha="left", va="center", fontsize=9.5, color=INK2)

# source well: the pipette aspirates 20 uL (its limit) before each dispense
SRC_X = -0.45
ax.text(SRC_X, 151, "Source well", ha="center", va="center", fontsize=10.5, fontweight="bold")
ax.add_patch(Rectangle((SRC_X - W / 2, 0), W, 70, fill=False, ec=INK2, lw=1.4, zorder=3))
ax.add_patch(Rectangle((SRC_X - W / 2, 0), W, 52, fc=C_WELL, ec="none", alpha=0.55, zorder=1))
pipette(SRC_X, 40, body_h=14)
ax.text(SRC_X, 98, "20 µL\ntip limit", ha="center", va="center", fontsize=9.5, color=INK2, linespacing=1.3)
ax.add_patch(FancyArrowPatch((SRC_X + 0.3, 80), (0.8, 122), connectionstyle="arc3,rad=-0.3",
                             arrowstyle="-|>", mutation_scale=14, color=INK2, lw=1.6, zorder=9))
ax.text(0.12, 128, "move 20 µL", ha="center", va="center", fontsize=9.5, color=INK2)

ax.text(AXIS_X + 0.05, 102, "100 µL target", ha="left", va="bottom", fontsize=9, color=INK2)
ax.plot([AXIS_X, XMAX], [100, 100], color=INK2, lw=0.8, ls=(0, (4, 4)), zorder=0)

# colour key (bands are centred on the nominal fill level)
ax.legend(
    handles=[
        Patch(fc=C_SYS, alpha=0.35, label="Systematic error (accuracy)"),
        Patch(fc=C_RAND, label="Random error (precision)"),
    ],
    loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=1, frameon=False, fontsize=9.5, labelcolor=INK2,
)

for ext in ("png", "svg"):
    fig.savefig(OUT_DIR / f"dispense_split_error.{ext}", dpi=200, facecolor=SURFACE)
print("wrote", OUT_DIR / "dispense_split_error.png")
