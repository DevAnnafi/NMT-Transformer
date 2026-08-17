from src.data.clean import normalize

def test_collapses_internal_whitespace():
    assert normalize("des Goldes  hinwiesen") == "des Goldes hinwiesen"

def test_strips_soft_hyphen():
    assert normalize("it\u00adwill") == "itwill"

def test_preserves_german_number_format():
    assert normalize("10.000 Dollar") == "10.000 Dollar"