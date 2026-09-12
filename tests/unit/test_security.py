from app.utils.hashing import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token, decode_token


class TestHachageMotDePasse:
    def test_hash_nest_pas_le_mot_de_passe_clair(self):
        hashed = hash_password("monmotdepasse")
        assert hashed != "monmotdepasse"
        assert len(hashed) > 20

    def test_bon_mot_de_passe_verifie(self):
        hashed = hash_password("correct123")
        assert verify_password("correct123", hashed) is True

    def test_mauvais_mot_de_passe_echoue(self):
        hashed = hash_password("correct123")
        assert verify_password("incorrect", hashed) is False

    def test_meme_mot_de_passe_hashes_differents(self):
        h1 = hash_password("identique")
        h2 = hash_password("identique")
        assert h1 != h2


class TestJWT:
    def test_token_contient_le_sujet(self):
        token = create_access_token(subject=42)
        payload = decode_token(token)
        assert payload["sub"] == "42"

    def test_token_access_a_le_bon_type(self):
        token = create_access_token(subject=1)
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_token_refresh_a_le_bon_type(self):
        token = create_refresh_token(subject=1)
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_token_expire_leve_une_exception(self):
        from datetime import timedelta
        from fastapi import HTTPException
        import pytest

        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc:
            decode_token(token)
        assert exc.value.status_code == 401
