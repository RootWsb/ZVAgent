import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "paper-download"
    / "scripts"
    / "download_paper.py"
)

spec = importlib.util.spec_from_file_location("download_paper", SCRIPT_PATH)
download_paper = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = download_paper
spec.loader.exec_module(download_paper)


def test_normalize_arxiv_id_from_common_forms():
    assert download_paper.normalize_arxiv_id("1706.03762") == "1706.03762"
    assert download_paper.normalize_arxiv_id("arXiv:1706.03762v7") == "1706.03762v7"
    assert download_paper.normalize_arxiv_id("https://arxiv.org/abs/1706.03762") == "1706.03762"
    assert download_paper.normalize_arxiv_id("https://arxiv.org/pdf/1706.03762.pdf") == "1706.03762"


def test_normalize_doi_from_common_forms():
    assert download_paper.normalize_doi("10.1038/s41586-021-03819-2") == "10.1038/s41586-021-03819-2"
    assert download_paper.normalize_doi("doi:10.1038/s41586-021-03819-2") == "10.1038/s41586-021-03819-2"
    assert download_paper.normalize_doi("https://doi.org/10.1038/s41586-021-03819-2") == "10.1038/s41586-021-03819-2"


def test_build_candidate_for_arxiv_prefers_pdf_endpoint():
    candidate = download_paper.build_candidate("https://arxiv.org/abs/1706.03762")
    assert candidate.source_type == "arxiv"
    assert candidate.download_url == "https://arxiv.org/pdf/1706.03762.pdf"
    assert candidate.filename_hint == "arxiv_1706.03762.pdf"


def test_safe_filename_adds_pdf_and_removes_unsafe_chars():
    assert download_paper.safe_filename("A/B: paper title") == "A_B_paper_title.pdf"


def test_sci_hub_mirror_is_rejected():
    assert download_paper.is_forbidden_source_url("https://www.sci-hub.vg/")
    try:
        download_paper.build_candidate("https://www.sci-hub.vg/10.1000/example.pdf")
    except ValueError as exc:
        assert "not supported" in str(exc)
    else:
        raise AssertionError("Sci-Hub mirror should be rejected")
