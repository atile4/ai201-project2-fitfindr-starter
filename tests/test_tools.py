from tools import create_fit_card, search_listings, suggest_outfit

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=20)
    assert all(item["price"] <= 20 for item in results)

def test_search_size_filter():
    results = search_listings("top", size="M", max_price=None)
    assert all("m" in item["size"].lower() for item in results)

def test_search_no_filters():
    # None filters should not crash and should return something
    results = search_listings("denim", size=None, max_price=None)
    assert isinstance(results, list)

from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

def test_suggest_outfit_returns_string():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_empty_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(result, str)
    assert len(result) > 0   # should return advice, not an empty string

def test_create_fit_card_returns_string():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    item = results[0]
    outfit = suggest_outfit(item, get_example_wardrobe())
    result = create_fit_card(outfit, item)
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    result = create_fit_card("", results[0])
    assert isinstance(result, str)
    assert result == "Couldn't generate a fit card — no outfit description was provided."