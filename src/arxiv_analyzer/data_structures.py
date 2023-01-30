from dataclasses import dataclass

NEW_LINE_REPLACEMENT = "bckslsh-n"
CSV_SEPARATOR = ";"


@dataclass
class PaperMetaData:

    id: str
    title: str
    date_published: str
    abstract: str
    categories: list[str]
