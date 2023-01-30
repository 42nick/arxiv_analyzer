from arxiv_analyzer.main import main, parse_args
from unittest import mock


def test_parse_args() -> None:
    args = parse_args(["--download", "--category", "cs.CV", "--offset", "0", "--max_results", "1"])
    assert args.download
    assert args.category == "cs.CV"
    assert args.offset == 0
    assert args.max_results == 1


def test_main() -> None:
    with mock.patch("arxiv_analyzer.main.parse_args") as mock_parse_args:
        mock_parse_args.return_value = mock.Mock(
            download=True, category="not existing category", offset=0, max_results=1
        )
        main()
        mock_parse_args.return_value = mock.Mock(
            download=False, category="not existing category", offset=0, max_results=1
        )
        main()
