import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
from matplotlib.patches import Rectangle

warnings.filterwarnings("ignore")

BG = "#F7F8FC"
PANEL = "#FFFFFF"
BORDER = "#E2E6EF"
GRID = "#EEF0F6"

TEXT = "#0F1B35"
SUBTEXT = "#3D4B66"
MUTED = "#8892A4"

BLUE = "#2563EB"
GREEN = "#16A34A"
RED = "#DC2626"
ORANGE = "#D97706"

VERDICT_COLORS = {
    "Accepted": GREEN,
    "Wrong Answer": RED,
    "TLE": ORANGE,
    "Runtime Error": "#7C3AED",
    "Compilation Error": "#EA580C",
    "MLE": "#0891B2",
    "Other": MUTED,
}

WEEKDAYS = ["Monday","Tuesday","Wednesday",
            "Thursday","Friday","Saturday","Sunday"]

rcParams["font.family"] = "DejaVu Sans"



def style_ax(ax, title=""):
    ax.set_facecolor(PANEL)

    for s in ax.spines.values():
        s.set_edgecolor(BORDER)

    ax.grid(axis="y", color=GRID)
    ax.tick_params(colors=MUTED, labelsize=8)

    if title:
        ax.set_title(title, fontsize=10, color=TEXT, loc="left")


def no_data(ax, msg="No data"):
    ax.set_facecolor(PANEL)
    ax.text(0.5, 0.5, msg, ha="center", va="center", color=MUTED)
    ax.set_xticks([])
    ax.set_yticks([])


# plots

def plot_rating(ax, contests_df, user):
    if contests_df.empty:
        no_data(ax, "No contests yet")
        return

    x = contests_df["contest_n"]
    y = contests_df["new_rating"]

    ax.plot(x, y, color=BLUE, linewidth=2)
    ax.fill_between(x, y, color=BLUE, alpha=0.1)

    i = np.argmax(y)
    ax.scatter(x.iloc[i], y.iloc[i], color=ORANGE)

    curr = user.get("rating")
    if curr:
        ax.axhline(curr, linestyle="--", color=GREEN)

    style_ax(ax, "Rating Progress")
    ax.set_xlabel("Contest #")
    ax.set_ylabel("Rating")


def plot_verdict(ax, subs_df):
    if subs_df.empty:
        no_data(ax)
        return

    counts = subs_df["verdict_label"].value_counts()
    colors = [VERDICT_COLORS.get(v, MUTED) for v in counts.index]

    ax.pie(counts.values, colors=colors, startangle=90,
           wedgeprops={"width": 0.5})

    total = counts.sum()
    ac = counts.get("Accepted", 0)

    ax.text(0, 0, f"{int(ac/total*100)}%", ha="center", color=GREEN)
    ax.set_title("Verdict")


def plot_difficulty(ax, subs_df):
    if subs_df.empty:
        no_data(ax)
        return

    ac = subs_df[subs_df["verdict"] == "OK"]

    if ac.empty:
        no_data(ax)
        return

    counts = ac["difficulty_bucket"].value_counts().sort_index()

    ax.bar(range(len(counts)), counts.values, color=BLUE)

    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts.index, rotation=30)

    style_ax(ax, "Difficulty")


def plot_monthly(ax, subs_df):
    if subs_df.empty:
        no_data(ax)
        return

    monthly = subs_df.groupby("month").size().reset_index(name="count")
    monthly = monthly.tail(18)

    x = range(len(monthly))
    ax.bar(x, monthly["count"], color=BLUE)

    if len(monthly) >= 3:
        avg = monthly["count"].rolling(3).mean()
        ax.plot(x, avg, color=ORANGE, linestyle="--")

    ax.set_xticks(x[::2])
    ax.set_xticklabels(monthly["month"].iloc[::2], rotation=30)

    style_ax(ax, "Submissions per Month")


def plot_heatmap(ax, subs_df):
    if subs_df.empty:
        no_data(ax)
        return

    pivot = (
        subs_df.groupby(["weekday", "hour"])
        .size()
        .unstack(fill_value=0)
        .reindex(WEEKDAYS)
        .reindex(columns=range(24), fill_value=0)
    )

    ax.imshow(pivot.values, aspect="auto", cmap="Blues")

    ax.set_yticks(range(len(WEEKDAYS)))
    ax.set_yticklabels([d[:3] for d in WEEKDAYS])

    ax.set_xticks(range(0, 24, 3))
    ax.set_xticklabels([f"{h}" for h in range(0, 24, 3)])

    ax.set_title("Activity Heatmap")


def plot_language(ax, subs_df):
    if subs_df.empty:
        no_data(ax)
        return

    counts = subs_df["lang_simple"].value_counts().head(5)

    ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%")
    ax.set_title("Languages")


def plot_tags(ax, subs_df):
    if subs_df.empty:
        no_data(ax)
        return

    ac = subs_df[subs_df["verdict"] == "OK"]

    if ac.empty:
        no_data(ax)
        return

    tags = ac["tags"].explode()
    tags = tags[tags.str.strip() != ""]

    top = tags.value_counts().head(10)

    ax.barh(range(len(top)), top.values, color=BLUE)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top.index)

    ax.invert_yaxis()
    style_ax(ax, "Top Tags")


def plot_delta(ax, contests_df):
    if contests_df.empty:
        no_data(ax)
        return

    d = contests_df["delta"]

    ax.hist(d[d >= 0], color=GREEN, alpha=0.7)
    ax.hist(d[d < 0], color=RED, alpha=0.7)

    ax.axvline(0, linestyle="--", color=MUTED)

    style_ax(ax, "Rating Change")


# dashboard

def build_dashboard(subs_df, contests_df, user, output_path):

    fig = plt.figure(figsize=(18, 14), facecolor=BG)

    gs = gridspec.GridSpec(3, 6, figure=fig)

    ax1 = fig.add_subplot(gs[0, :4])
    ax2 = fig.add_subplot(gs[0, 4])
    ax3 = fig.add_subplot(gs[0, 5])

    ax4 = fig.add_subplot(gs[1, :3])
    ax5 = fig.add_subplot(gs[1, 3:])

    ax6 = fig.add_subplot(gs[2, :2])
    ax7 = fig.add_subplot(gs[2, 2:4])
    ax8 = fig.add_subplot(gs[2, 4:])

    plot_rating(ax1, contests_df, user)
    plot_verdict(ax2, subs_df)
    plot_difficulty(ax3, subs_df)

    plot_monthly(ax4, subs_df)
    plot_heatmap(ax5, subs_df)

    plot_language(ax6, subs_df)
    plot_tags(ax7, subs_df)
    plot_delta(ax8, contests_df)

    handle = user.get("handle", "?")
    rating = user.get("rating", "-")
    rank = user.get("rank", "-")

    fig.suptitle(
        f"{handle} | Rating: {rating} ({rank})",
        fontsize=13,
        color=TEXT
    )

    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Saved {output_path}")