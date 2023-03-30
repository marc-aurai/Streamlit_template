import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.analyse_plots import plot_all_axes

df = pd.read_csv("./espn_scraper/scraper_data/articles_5000_notna.csv", sep=";")
df["word_count"] = df["article"].apply(lambda x: len(x.split()))

sns.set(
    rc={
        "axes.facecolor": "#100c44",
        "figure.facecolor": "#100c44",
        "xtick.color": "white",
        "ytick.color": "white",
        "text.color": "white",
        "axes.labelcolor": "white",
        "font.size": 30,
        "axes.titlesize": 30,
        "axes.labelsize": 30,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20,
    }
)


fig = plt.figure(figsize=(16, 50))
ax1 = fig.add_subplot(5, 1, 1)
ax2 = fig.add_subplot(5, 1, 2)
ax3 = fig.add_subplot(5, 1, 3)
ax4 = fig.add_subplot(5, 1, 4)
ax5 = fig.add_subplot(5, 1, 5)
plt.subplots_adjust(hspace=0.5)

ax1, ax2, ax3, ax4, ax5 = plot_all_axes(
    ax1=ax1,
    ax2=ax2,
    ax3=ax3,
    ax4=ax4,
    ax5=ax5,
    df=df,
    amount_words=10,
)
plt.show()