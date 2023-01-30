import pandas as pd
from arxiv_analyzer.data_structures import CSV_SEPARATOR

from arxiv_analyzer.parameters import ARXIV_DATA_FILENAME, DATA_ROOT


def read_data_from_csv(file_name: str) -> pd.DataFrame:
    data_path = DATA_ROOT / file_name
    return pd.read_csv(data_path, sep=CSV_SEPARATOR)


def find_key_words_in_abstracts(key_words: list[str], data_frame: pd.DataFrame, lower: bool = True) -> pd.DataFrame:

    abstract_lowered = data_frame["abstract"].str.lower()
    key_word_mask = abstract_lowered.str.contains(key_words[0])
    for key_word in key_words[1:]:
        key_word_mask = key_word_mask & abstract_lowered.str.contains(key_word)
    return data_frame[key_word_mask]


def main():
    df = read_data_from_csv(ARXIV_DATA_FILENAME)
    subset = find_key_words_in_abstracts(["bird", "eye", "view"], df)

    print(subset["date_published"].min())
    for a in subset["title"]:
        print(a)


if __name__ == "__main__":
    main()
