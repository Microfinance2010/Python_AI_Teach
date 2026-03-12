import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Explizite, helle Defaults (robust gegen vorherige Dark-Styles)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "text.color": "#222222",
    "axes.labelcolor": "#222222",
    "axes.edgecolor": "#666666",
    "xtick.color": "#222222",
    "ytick.color": "#222222",
    "legend.labelcolor": "#222222",
})

fig, ax = plt.subplots(figsize=(9, 6))

# Dezente Quadrantenflächen
ax.add_patch(Rectangle((0, 0), 5, 5, facecolor="#f7f7f7", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((5, 0), 5, 5, facecolor="#f2f8ff", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((0, 5), 5, 5, facecolor="#fff8f2", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((5, 5), 5, 5, facecolor="#f3fbf4", edgecolor="none", zorder=0))

# Referenzlinien
ax.axvline(5, color="#bdbdbd", linewidth=1)
ax.axhline(5, color="#bdbdbd", linewidth=1)

# Punkte (farbenblind-freundlich)
systems = {
    "Tightly controlled workflow\n(high tool freedom)": (9, 2, "#0072B2"),
    "Fully autonomous system": (9, 9, "#009E73"),
    "Standard chatbot\n(high process freedom,\nlimited tools)": (2, 8, "#D55E00"),
}

for label, (x, y, color) in systems.items():
    ax.scatter(
        x, y, s=130, color=color, edgecolor="black", linewidth=0.6, label=label, zorder=3
    )
    ax.annotate(
        label,
        (x, y),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=9,
        color="#222222",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#cccccc", alpha=0.9),
    )

# Achsen, Titel, Ticks
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_xlabel("Tool autonomy (low \u2192 high)", color="#222222")
ax.set_ylabel("Process structure autonomy (low \u2192 high)", color="#222222")
ax.set_title("Agentic AI Design Space", color="#111111")

ax.set_xticks([0, 5, 10], labels=["Low", "Medium", "High"])
ax.set_yticks([0, 5, 10], labels=["Low", "Medium", "High"])

# Gitter und Spines
ax.grid(True, linestyle="-", linewidth=0.6, alpha=0.2, color="#888888")
for spine in ax.spines.values():
    spine.set_color("#666666")
    spine.set_linewidth(0.9)

# Legende
legend = ax.legend(title="Example systems", loc="lower left", frameon=True)
legend.get_frame().set_facecolor("white")
legend.get_frame().set_edgecolor("#cccccc")
legend.get_frame().set_alpha(0.95)

plt.tight_layout()

# Export für Slides / Publikation
plt.savefig("autonomy_plot.png", dpi=300, bbox_inches="tight")
plt.savefig("autonomy_plot.svg", bbox_inches="tight")
plt.savefig("autonomy_plot.pdf", bbox_inches="tight")

plt.show()