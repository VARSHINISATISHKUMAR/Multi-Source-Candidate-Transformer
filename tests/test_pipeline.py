from normalize import normalize_phone


def test_phone_normalization():

    phone = normalize_phone("+91 98765 43210")

    assert phone == "+919876543210"