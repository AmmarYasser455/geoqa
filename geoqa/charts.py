"""
Charts module: static matplotlib visualizations for GeoQA reports.

Generates publication-quality charts for:
- Geometry type distribution (pie chart)
- Attribute completeness (horizontal bar chart)
- Quality score gauge (donut chart)
- Area/length distribution (histogram)
- Null heatmap (matrix visualization)

Author: Ammar Yasser Abdalazim
"""

from __future__ import annotations

import base64
import io
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Use non-interactive backend for report generation
matplotlib.use("Agg")

# ── GeoQA chart palette ────────────────────────────────────────────────
PALETTE = {
    "primary": "#2563eb",
    "success": "#16a34a",
    "warning": "#f59e0b",
    "danger": "#dc2626",
    "info": "#0891b2",
    "muted": "#94a3b8",
    "bg": "#f8fafc",
    "text": "#1e293b",
    "grid": "#e2e8f0",
}

QUALITY_COLORS = {
    "excellent": "#16a34a",  # green  ≥ 90
    "good": "#65a30d",  # lime   ≥ 75
    "fair": "#f59e0b",  # amber  ≥ 50
    "poor": "#dc2626",  # red    < 50
}


def _quality_color(score: float) -> str:
    """Return color based on quality score."""
    if score >= 90:
        return QUALITY_COLORS["excellent"]
    if score >= 75:
        return QUALITY_COLORS["good"]
    if score >= 50:
        return QUALITY_COLORS["fair"]
    return QUALITY_COLORS["poor"]


def _fig_to_base64(fig: plt.Figure, dpi: int = 150) -> str:
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(
        buf, format="png", dpi=dpi, bbox_inches="tight", facecolor=PALETTE["bg"], edgecolor="none"
    )
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _fig_to_html_img(fig: plt.Figure, dpi: int = 150, alt: str = "chart") -> str:
    """Convert a matplotlib figure to an <img> HTML tag."""
    b64 = _fig_to_base64(fig, dpi=dpi)
    return (
        f'<img src="data:image/png;base64,{b64}" alt="{alt}" style="max-width:100%;height:auto;" />'
    )


# ────────────────────────────────────────────────────────────────────────
#  Chart generators
# ────────────────────────────────────────────────────────────────────────


def quality_gauge(score: float, size: tuple[float, float] = (4, 4)) -> plt.Figure:
    """Create a donut-style quality score gauge.

    Args:
        score: Quality score (0-100).
        size: (width, height) in inches.

    Returns:
        matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=size, subplot_kw={"aspect": "equal"})
    fig.patch.set_facecolor(PALETTE["bg"])

    color = _quality_color(score)
    remaining = 100 - score
    wedges, _ = ax.pie(
        [score, remaining],
        startangle=90,
        colors=[color, PALETTE["grid"]],
        wedgeprops={"width": 0.35, "edgecolor": PALETTE["bg"], "linewidth": 2},
    )

    # Center label
    ax.text(
        0,
        0.08,
        f"{score:.0f}",
        ha="center",
        va="center",
        fontsize=28,
        fontweight="bold",
        color=color,
    )
    ax.text(0, -0.18, "Quality Score", ha="center", va="center", fontsize=9, color=PALETTE["text"])

    ax.set_title("")
    return fig


def geometry_type_pie(
    type_counts: dict[str, int],
    size: tuple[float, float] = (5, 4),
) -> plt.Figure:
    """Create a pie chart of geometry type distribution.

    Args:
        type_counts: Dict mapping geometry type name to count.
        size: (width, height) in inches.

    Returns:
        matplotlib Figure.
    """
    if not type_counts:
        fig, ax = plt.subplots(figsize=size)
        ax.text(
            0.5,
            0.5,
            "No geometry data",
            ha="center",
            va="center",
            fontsize=12,
            color=PALETTE["muted"],
        )
        ax.axis("off")
        return fig

    labels = list(type_counts.keys())
    values = list(type_counts.values())
    colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))

    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(PALETTE["bg"])

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops={"edgecolor": PALETTE["bg"], "linewidth": 1.5},
        pctdistance=0.75,
    )

    for t in texts:
        t.set_fontsize(9)
        t.set_color(PALETTE["text"])
    for t in autotexts:
        t.set_fontsize(8)
        t.set_fontweight("bold")

    ax.set_title(
        "Geometry Type Distribution", fontsize=11, fontweight="bold", color=PALETTE["text"], pad=12
    )

    return fig


def attribute_completeness_bar(
    completeness: dict[str, float],
    size: tuple[float, float] = (7, None),
) -> plt.Figure:
    """Create a horizontal bar chart of attribute completeness.

    Args:
        completeness: Dict mapping column name to completeness percentage (0-100).
        size: (width, height) in inches. Height auto-calculated if None.

    Returns:
        matplotlib Figure.
    """
    if not completeness:
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.text(
            0.5,
            0.5,
            "No attribute data",
            ha="center",
            va="center",
            fontsize=12,
            color=PALETTE["muted"],
        )
        ax.axis("off")
        return fig

    # Sort by completeness ascending (worst at top)
    sorted_items = sorted(completeness.items(), key=lambda x: x[1])
    names = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    # Truncate long column names
    display_names = [n[:25] + "…" if len(n) > 25 else n for n in names]

    height = size[1] if size[1] is not None else max(3, len(names) * 0.4 + 1)
    fig, ax = plt.subplots(figsize=(size[0], height))
    fig.patch.set_facecolor(PALETTE["bg"])

    # Color based on completeness
    bar_colors = []
    for v in values:
        if v >= 95:
            bar_colors.append(QUALITY_COLORS["excellent"])
        elif v >= 80:
            bar_colors.append(QUALITY_COLORS["good"])
        elif v >= 50:
            bar_colors.append(QUALITY_COLORS["fair"])
        else:
            bar_colors.append(QUALITY_COLORS["poor"])

    bars = ax.barh(
        display_names, values, color=bar_colors, edgecolor=PALETTE["bg"], linewidth=0.5, height=0.65
    )

    # Value labels
    for bar, val in zip(bars, values):
        ax.text(
            min(val + 1, 101),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            va="center",
            fontsize=8,
            color=PALETTE["text"],
        )

    ax.set_xlim(0, 110)
    ax.set_xlabel("Completeness (%)", fontsize=9, color=PALETTE["text"])
    ax.set_title(
        "Attribute Completeness", fontsize=11, fontweight="bold", color=PALETTE["text"], pad=12
    )
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(PALETTE["grid"])
    ax.spines["left"].set_color(PALETTE["grid"])
    ax.xaxis.grid(True, color=PALETTE["grid"], linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig


def distribution_histogram(
    values: list[float] | np.ndarray,
    label: str = "Value",
    units: str = "",
    bins: int = 30,
    size: tuple[float, float] = (7, 4),
) -> plt.Figure:
    """Create a histogram showing the distribution of a numeric series.

    Args:
        values: Numeric values to plot.
        label: Human-readable label (e.g. "Area", "Length").
        units: Unit string appended to x-axis label.
        bins: Number of histogram bins.
        size: (width, height) in inches.

    Returns:
        matplotlib Figure.
    """
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]

    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(PALETTE["bg"])

    if len(arr) == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12, color=PALETTE["muted"])
        ax.axis("off")
        return fig

    ax.hist(
        arr, bins=bins, color=PALETTE["primary"], edgecolor=PALETTE["bg"], linewidth=0.5, alpha=0.85
    )

    xlabel = f"{label} ({units})" if units else label
    ax.set_xlabel(xlabel, fontsize=9, color=PALETTE["text"])
    ax.set_ylabel("Frequency", fontsize=9, color=PALETTE["text"])
    ax.set_title(
        f"{label} Distribution", fontsize=11, fontweight="bold", color=PALETTE["text"], pad=12
    )

    # Stats annotation
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    ax.axvline(
        mean_val,
        color=PALETTE["danger"],
        linestyle="--",
        linewidth=1,
        label=f"Mean: {mean_val:.4g}",
    )
    ax.axvline(
        median_val,
        color=PALETTE["success"],
        linestyle="-.",
        linewidth=1,
        label=f"Median: {median_val:.4g}",
    )
    ax.legend(fontsize=8, framealpha=0.8)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(PALETTE["grid"])
    ax.spines["left"].set_color(PALETTE["grid"])
    ax.tick_params(axis="both", labelsize=8)

    fig.tight_layout()
    return fig


def null_heatmap(
    null_counts: dict[str, int],
    total_rows: int,
    size: tuple[float, float] = (7, None),
) -> plt.Figure:
    """Create a heatmap-style chart showing null counts per column.

    Args:
        null_counts: Dict mapping column name to null count.
        total_rows: Total number of rows in the dataset.
        size: (width, height) in inches. Height auto-calculated if None.

    Returns:
        matplotlib Figure.
    """
    if not null_counts or total_rows == 0:
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.text(
            0.5, 0.5, "No null data", ha="center", va="center", fontsize=12, color=PALETTE["muted"]
        )
        ax.axis("off")
        return fig

    # Filter to columns that actually have nulls
    has_nulls = {k: v for k, v in null_counts.items() if v > 0}
    if not has_nulls:
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.text(
            0.5,
            0.5,
            "No null values — all columns complete ✓",
            ha="center",
            va="center",
            fontsize=11,
            color=QUALITY_COLORS["excellent"],
        )
        ax.axis("off")
        return fig

    sorted_items = sorted(has_nulls.items(), key=lambda x: x[1], reverse=True)
    names = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    pcts = [c / total_rows * 100 for c in counts]

    display_names = [n[:25] + "…" if len(n) > 25 else n for n in names]

    height = size[1] if size[1] is not None else max(3, len(names) * 0.45 + 1)
    fig, ax = plt.subplots(figsize=(size[0], height))
    fig.patch.set_facecolor(PALETTE["bg"])

    # Gradient from amber to red based on severity
    colors = []
    for pct in pcts:
        if pct >= 50:
            colors.append(QUALITY_COLORS["poor"])
        elif pct >= 20:
            colors.append(QUALITY_COLORS["fair"])
        else:
            colors.append(PALETTE["warning"])

    bars = ax.barh(
        display_names, pcts, color=colors, edgecolor=PALETTE["bg"], linewidth=0.5, height=0.65
    )

    for bar, pct, count in zip(bars, pcts, counts):
        ax.text(
            pct + 0.8,
            bar.get_y() + bar.get_height() / 2,
            f"{count:,} ({pct:.1f}%)",
            va="center",
            fontsize=8,
            color=PALETTE["text"],
        )

    ax.set_xlabel("Null Percentage (%)", fontsize=9, color=PALETTE["text"])
    ax.set_title(
        "Null Values by Column", fontsize=11, fontweight="bold", color=PALETTE["text"], pad=12
    )
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(PALETTE["grid"])
    ax.spines["left"].set_color(PALETTE["grid"])

    fig.tight_layout()
    return fig


def checks_summary_bar(
    checks: list[dict[str, Any]],
    size: tuple[float, float] = (7, 3.5),
) -> plt.Figure:
    """Create a horizontal bar chart summarizing quality check results.

    Args:
        checks: List of dicts with keys 'Check', 'Status', 'Count', 'Severity'.
        size: (width, height) in inches.

    Returns:
        matplotlib Figure.
    """
    if not checks:
        fig, ax = plt.subplots(figsize=size)
        ax.text(
            0.5, 0.5, "No check data", ha="center", va="center", fontsize=12, color=PALETTE["muted"]
        )
        ax.axis("off")
        return fig

    names = [c["Check"] for c in checks]
    statuses = [c["Status"] for c in checks]

    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor(PALETTE["bg"])

    colors = []
    for s in statuses:
        if s == "PASS":
            colors.append(QUALITY_COLORS["excellent"])
        elif s == "WARN":
            colors.append(QUALITY_COLORS["fair"])
        else:
            colors.append(QUALITY_COLORS["poor"])

    # Simple indicator bars (binary: 1 for each check)
    ax.barh(
        names, [1] * len(names), color=colors, edgecolor=PALETTE["bg"], linewidth=0.5, height=0.6
    )

    for i, (status, check) in enumerate(zip(statuses, checks)):
        detail_txt = check.get("Details", "")
        if len(detail_txt) > 50:
            detail_txt = detail_txt[:47] + "..."
        ax.text(
            0.5,
            i,
            f"{status}  —  {detail_txt}",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white",
        )

    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title(
        "Quality Check Results", fontsize=11, fontweight="bold", color=PALETTE["text"], pad=12
    )
    ax.tick_params(axis="y", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color(PALETTE["grid"])
    ax.invert_yaxis()

    fig.tight_layout()
    return fig


# ────────────────────────────────────────────────────────────────────────
#  Convenience: generate all charts for a GeoProfile
# ────────────────────────────────────────────────────────────────────────


def generate_all_charts(profile) -> dict[str, str]:
    """Generate all chart images for a GeoProfile as base64-encoded PNGs.

    Args:
        profile: A GeoProfile instance.

    Returns:
        Dict mapping chart name to base64-encoded PNG string.
    """
    charts: dict[str, str] = {}

    # Quality gauge
    fig = quality_gauge(profile.quality_score)
    charts["quality_gauge"] = _fig_to_base64(fig)

    # Geometry type distribution
    geom_types = profile.geometry_results.get("geometry_types", {})
    if geom_types:
        fig = geometry_type_pie(geom_types)
        charts["geometry_types"] = _fig_to_base64(fig)

    # Attribute completeness
    completeness = profile.attribute_results.get("completeness", {})
    if completeness:
        fig = attribute_completeness_bar(completeness)
        charts["attribute_completeness"] = _fig_to_base64(fig)

    # Null heatmap
    null_counts = profile.attribute_results.get("null_counts", {})
    if null_counts:
        fig = null_heatmap(null_counts, profile.feature_count)
        charts["null_heatmap"] = _fig_to_base64(fig)

    # Checks summary
    checks_df = profile.quality_checks()
    checks_list = checks_df.to_dict("records")
    fig = checks_summary_bar(checks_list)
    charts["checks_summary"] = _fig_to_base64(fig)

    # Distribution histograms (area or length depending on geometry type)
    dom_type = profile.geometry_type.lower()
    if "polygon" in dom_type:
        areas = profile.gdf.geometry.apply(
            lambda g: g.area if g is not None and not g.is_empty else 0
        ).values
        if np.any(areas > 0):
            fig = distribution_histogram(
                areas, label="Area", units=profile.spatial_results.get("crs_units", "")
            )
            charts["area_distribution"] = _fig_to_base64(fig)

        perimeters = profile.gdf.geometry.apply(
            lambda g: g.length if g is not None and not g.is_empty else 0
        ).values
        if np.any(perimeters > 0):
            fig = distribution_histogram(
                perimeters, label="Perimeter", units=profile.spatial_results.get("crs_units", "")
            )
            charts["perimeter_distribution"] = _fig_to_base64(fig)

    elif "line" in dom_type:
        lengths = profile.gdf.geometry.apply(
            lambda g: g.length if g is not None and not g.is_empty else 0
        ).values
        if np.any(lengths > 0):
            fig = distribution_histogram(
                lengths, label="Length", units=profile.spatial_results.get("crs_units", "")
            )
            charts["length_distribution"] = _fig_to_base64(fig)

    return charts
