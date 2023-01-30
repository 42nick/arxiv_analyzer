import sys
from arxiv_analyzer.down_load_cv_related_papers import download_cv_related_paper_metadata
import argparse


def parse_args(args: list[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--download", action="store_true", help="Downloads metadata from arxiv based on the given categories."
    )
    parser.add_argument("--category", type=str, help="The category to download from arxiv.", default="cs.CV")
    parser.add_argument(
        "--offset", type=int, help="The offset to start downloading from in case a previous download failed.", default=0
    )
    parser.add_argument("--max_results", type=int, help="The maximum number of results to query.", default=1000000)

    return parser.parse_args(args)


def main() -> None:
    """
    The core function of this awesome project.
    """

    args = parse_args(sys.argv[1:])

    if args.download:
        download_cv_related_paper_metadata(category=args.category, offset=args.offset, max_results=args.max_results)


if __name__ == "__main__":
    main()
