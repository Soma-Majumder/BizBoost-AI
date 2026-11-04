import json

import pytest

from findings import (
    Category,
    Finding,
    InvalidFindingError,
    Source,
    Status,
    finding,
    findings_to_json_data,
    unavailable,
)

EXAMPLE = {
    "check_id": "technical.meta_description",
    "category": "technical_seo",
    "page": "https://example.com/",
    "status": "fail",
    "evidence": "Meta description tag is missing",
    "source": "crawler",
    "weight": 3,
}


def test_architecture_doc_example_round_trips():
    item = Finding.from_dict(EXAMPLE)
    assert item.category is Category.TECHNICAL_SEO
    assert item.status is Status.FAIL
    assert item.to_dict() == EXAMPLE


def test_to_dict_is_json_serializable():
    data = findings_to_json_data([Finding.from_dict(EXAMPLE)])
    assert json.loads(json.dumps(data)) == [EXAMPLE]


def test_helper_defaults():
    item = finding("keyword.title", Category.KEYWORD_OPTIMIZATION, "pass", "Title found")
    assert item.source is Source.CRAWLER
    assert item.weight == 1
    assert item.page is None


def test_unavailable_is_not_measured_and_keeps_reason():
    item = unavailable("credibility.backlinks", "credibility_backlinks", "No backlink provider")
    assert item.status is Status.UNAVAILABLE
    assert not item.is_measured
    assert item.evidence == "No backlink provider"


@pytest.mark.parametrize("status", ["pass", "warn", "fail"])
def test_measured_statuses(status):
    assert finding("x.y", "local_seo", status, "e").is_measured


@pytest.mark.parametrize(
    "change",
    [
        {"status": "maybe"},
        {"category": "seo"},
        {"source": "guess"},
        {"check_id": ""},
        {"check_id": "   "},
        {"evidence": ""},
        {"evidence": "   "},
        {"weight": 0},
        {"weight": -1},
        {"weight": 1.5},
        {"weight": True},
        {"page": 123},
    ],
)
def test_invalid_findings_are_rejected(change):
    with pytest.raises(InvalidFindingError):
        Finding.from_dict({**EXAMPLE, **change})


def test_missing_and_unknown_fields_are_rejected():
    missing = {k: v for k, v in EXAMPLE.items() if k != "evidence"}
    with pytest.raises(InvalidFindingError):
        Finding.from_dict(missing)
    with pytest.raises(InvalidFindingError):
        Finding.from_dict({**EXAMPLE, "score": 5})


def test_findings_are_immutable():
    item = Finding.from_dict(EXAMPLE)
    with pytest.raises(Exception):
        item.status = Status.PASS


def test_page_is_optional_for_site_wide_checks():
    item = Finding.from_dict({k: v for k, v in EXAMPLE.items() if k != "page"})
    assert item.page is None
    assert item.to_dict()["page"] is None
