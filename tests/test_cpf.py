from app.cpf import format_cpf, is_valid, mask, normalize, region


def test_normalize_strips_non_digits():
    assert normalize("111.444.777-35") == "11144477735"
    assert normalize("  11144477735  ") == "11144477735"


def test_is_valid_accepts_known_valid_cpf():
    assert is_valid("111.444.777-35") is True
    assert is_valid("11144477735") is True


def test_is_valid_rejects_check_digit_mismatch():
    assert is_valid("11144477734") is False


def test_is_valid_rejects_repeated_digits():
    assert is_valid("00000000000") is False
    assert is_valid("11111111111") is False


def test_is_valid_rejects_wrong_length():
    assert is_valid("123") is False
    assert is_valid("") is False


def test_format_cpf():
    assert format_cpf("11144477735") == "111.444.777-35"


def test_mask_hides_first_block_and_check_digits():
    assert mask("11144477735") == "***.444.777-**"


def test_region_returns_state_group():
    assert region("11144477735") is not None
