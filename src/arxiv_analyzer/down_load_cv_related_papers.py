from typing import Generator
import arxiv
import pandas as pd

from arxiv_analyzer.data_structures import CSV_SEPARATOR, NEW_LINE_REPLACEMENT, PaperMetaData
from arxiv_analyzer.parameters import DATA_ROOT, ARXIV_DATA_FILENAME
from arxiv import Client, Result, Search


class ExtendedClient(Client):
    def results(self, search: Search, offset: int = 0) -> Generator[Result, None, None]:
        """
        Uses this client configuration to fetch one page of the search results
        at a time, yielding the parsed `Result`s, until `max_results` results
        have been yielded or there are no more search results.

        If all tries fail, raises an `UnexpectedEmptyPageError` or `HTTPError`.

        For more on using generators, see
        [Generators](https://wiki.python.org/moin/Generators).
        """
        # total_results may be reduced according to the feed's
        # opensearch:totalResults value.
        total_results = search.max_results
        first_page = True
        while offset < total_results:
            page_size = min(self.page_size, search.max_results - offset)

            page_url = self._format_url(search, offset, page_size)
            feed = self._parse_feed(page_url, first_page)
            if first_page:
                # NOTE: this is an ugly fix for a known bug. The totalresults
                # value is set to 1 for results with zero entries. If that API
                # bug is fixed, we can remove this conditional and always set
                # `total_results = min(...)`.
                if len(feed.entries) == 0:
                    total_results = 0
                else:
                    total_results = min(total_results, int(feed.feed.opensearch_totalresults))
                # Subsequent pages are not the first page.
                first_page = False
            # Update offset for next request: account for received results.
            offset += len(feed.entries)
            # Yield query results until page is exhausted.
            for entry in feed.entries:
                try:
                    yield Result._from_feed_entry(entry)
                except Result.MissingFieldError:
                    continue


def gather_data_from_result(result: arxiv.Result) -> PaperMetaData:
    return PaperMetaData(
        # removing the static arxiv adress and the version number
        id=result.entry_id.split("/")[-1].split("v")[0],
        title=result.title,
        date_published=result.published,
        abstract=result.summary,
        categories=result.categories,
    )


def convert_paper_list_to_dataframe(paper_list: list[PaperMetaData]) -> pd.DataFrame:
    return pd.DataFrame.from_records([paper.__dict__ for paper in paper_list])


def store_data_frame_to_csv(data_frame: pd.DataFrame, file_name: str):

    # replace \n with weird unicode character
    data_frame["abstract"] = data_frame["abstract"].str.replace("\n", NEW_LINE_REPLACEMENT).str.replace(";", "")
    data_frame["title"] = data_frame["title"].str.replace("\n", NEW_LINE_REPLACEMENT).str.replace(";", "")

    data_path = DATA_ROOT / file_name
    if not data_path.exists():
        data_path.touch()
        data_frame.to_csv(data_path, index=False, sep=CSV_SEPARATOR)
    else:
        data_frame.to_csv(data_path, index=False, mode="a", header=False, sep=CSV_SEPARATOR)


def download_cv_related_paper_metadata(category: str = "cs.CV", max_results: int = 1000000, offset: int = 0):
    search = arxiv.Search(query=f"cat:{category}", max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)

    cnt = offset
    num_intermediate_results = 50

    paper_list: list[PaperMetaData] = []

    for result in ExtendedClient(num_retries=10, page_size=num_intermediate_results, delay_seconds=5).results(
        search, offset=offset
    ):
        paper_list.append(gather_data_from_result(result))
        cnt += 1
        print(cnt)

        if cnt % num_intermediate_results == 0:
            data_frame = convert_paper_list_to_dataframe(paper_list)
            store_data_frame_to_csv(data_frame, ARXIV_DATA_FILENAME)
            paper_list = []
