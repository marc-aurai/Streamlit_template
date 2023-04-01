import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import STOPWORDS, WordCloud
from nltk.probability import FreqDist

from analysis.utils.analysis import get_corpus, most_common_words, Bigrams, Trigrams


def woorden_per_samenvatting_plot(
    ax1: plt.Axes, df: pd.DataFrame, cup: list
) -> plt.Axes:
    sns.histplot(
        df.loc[df.cup == cup[0]],
        x="word_count",
        kde=True,
        color="#FFFFFF",
        binwidth=2,
        alpha=0.9,
        ax=ax1,
        bins=500
    )
    ax1.set_title("Totaal aantal woorden\n per samenvatting")
    ax1.set_xlabel("Aantal woorden")
    ax1.set_ylabel("Aantal samenvatting\nmet dit aantal woorden")
    return ax1


def meest_voorkomende_woorden_plot(
    ax2: plt.Axes, df: pd.DataFrame, amount_words: int, cup: list
) -> plt.Axes:
    corpus = get_corpus(df)
    words, freq = most_common_words(corpus, amount_words=amount_words)
    sns.barplot(x=freq, y=words, color="#FFFFFF", ax=ax2)
    ax2.set_title("Top {} meest voorkomende woorden".format(amount_words))
    ax2.set_xlabel("Frequentie")
    ax2.set_ylabel("Woord combinatie")
    return ax2


def wordcloud_plot(ax3: plt.Axes, df: pd.DataFrame, amount_words: int, cup: list) -> plt.Axes:
    article_text = df.article.values
    wordcloud = WordCloud(
        max_font_size=60,
        max_words=amount_words,
        width=500,
        height=200,
        stopwords=STOPWORDS,
        background_color="#FFFFFF",
    ).generate(
        str(article_text)
    )
    ax3.imshow(wordcloud)
    ax3.grid(visible=False)
    ax3.set_xticks([])
    ax3.set_yticks([])
    return ax3


def bigrams_plot(ax4: plt.Axes, df: pd.DataFrame, amount_words: int, cup: list) -> plt.Axes:
    ngram_freq, ngram_type = Bigrams(df)
    sns.barplot(
        x=ngram_freq["frequency"][:amount_words],
        y=ngram_freq["ngram"][:amount_words],
        color="#FFFFFF",
        ax=ax4,
    )
    ax4.set_title("Top {} meest voorkomende {}".format(amount_words, ngram_type))
    ax4.set_xlabel("Frequentie")
    ax4.set_ylabel("Bigram combinatie")
    return ax4


def trigrams_plot(ax5: plt.Axes, df: pd.DataFrame, amount_words: int, cup: list) -> plt.Axes:
    ngram_freq, ngram_type = Trigrams(df)
    sns.barplot(
        x=ngram_freq["frequency"][:amount_words],
        y=ngram_freq["ngram"][:amount_words],
        color="#FFFFFF",
        ax=ax5,
    )
    ax5.set_title("Top {} meest voorkomende {}".format(amount_words, ngram_type))
    ax5.set_xlabel("Frequentie")
    ax5.set_ylabel("Trigram combinatie")
    return ax5


def plot_all_axes(
    ax1: plt.Axes,
    ax2: plt.Axes,
    #ax3: plt.Axes,
    ax4: plt.Axes,
    ax5: plt.Axes,
    df: pd.DataFrame,
    amount_words: int,
    cup_selected: list,
) -> plt.Axes:
    ax1 = woorden_per_samenvatting_plot(ax1, df, cup_selected)
    ax2 = meest_voorkomende_woorden_plot(ax2, df, amount_words, cup_selected)
    #ax3 = wordcloud_plot(ax3, df, amount_words)
    ax4 = bigrams_plot(ax4, df, amount_words, cup_selected)
    ax5 = trigrams_plot(ax5, df, amount_words, cup_selected)
    return ax1, ax2, ax4, ax5