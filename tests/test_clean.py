from src.data.clean import normalize, has_no_giant_token

def test_collapses_internal_whitespace():
    assert normalize("des Goldes  hinwiesen") == "des Goldes hinwiesen"

def test_strips_soft_hyphen():
    assert normalize("it\u00adwill") == "itwill"

def test_preserves_german_number_format():
    assert normalize("10.000 Dollar") == "10.000 Dollar"

def test_giant_token_rejected():
    assert not has_no_giant_token(
        "WelcheLektionenlassensichnunausdiesembetrüblichenStandderDingelernen?", 40
    )

def test_long_german_compound_accepted():
    assert has_no_giant_token("Geschwindigkeitsbegrenzung", 40)