import itertools
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

plt.rcParams["figure.facecolor"] = "#100c44"
plt.rcParams["savefig.facecolor"] = "#100c44"
plt.rcParams["text.color"] = "#FFFFFF"


def plot_winstreak(streak: str, title_plt: str):
    figure(figsize=(3, 1), dpi=60)
    x = [0, 1, 2, 3, 4, 5]
    y = [0, 0, 0, 0, 0, 0]
    color_list = [
        "lightgray"
        if match_status == "D"
        else "r"
        if match_status == "L"
        else "g"
        if match_status == "W"
        else "#100c44"
        for match_status in list(streak)
    ]
    streak_list = [
        "Gelijk"
        if match_status == "D"
        else "Lose"
        if match_status == "L"
        else "Win"
        if match_status == "W"
        else "None"
        for match_status in list(streak)
    ]

    colors = itertools.cycle(color_list)
    for x_, y_, streak in zip(x, y, streak_list):
        plt.scatter(x_, y_, color=next(colors))
        plt.title(title_plt, fontsize=18)
        plt.text(x_ + 0.03, y_ + 0.03, streak, fontsize=9, rotation=45)
    plt.axis("off")
    return plt
