"""Testes para o módulo client.py."""

import time
from unittest.mock import MagicMock, patch

import pytest
import requests

from f1.client import OpenF1Client


@pytest.fixture()
def client() -> OpenF1Client:
    """Cliente configurado para testes: sem throttle, retry rápido."""
    return OpenF1Client(
        base_url="https://api.test.local/v1/",
        timeout=5,
        min_interval=0.0,
        retry_waits=[0.0, 0.0, 0.0],
    )


def _mock_response(status_code: int, json_data: object = None) -> MagicMock:
    """Cria um mock de requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or []
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


class TestOpenF1ClientGet:
    def test_successful_response_returns_list(self, client: OpenF1Client) -> None:
        """Deve retornar lista de dicts em resposta bem-sucedida."""
        expected = [{"session_key": 1, "session_name": "Race"}]

        with patch("requests.get", return_value=_mock_response(200, expected)) as mock_get:
            result = client.get("sessions", params={"year": 2023})

        assert result == expected
        mock_get.assert_called_once_with(
            "https://api.test.local/v1/sessions",
            params={"year": 2023},
            timeout=5,
        )

    def test_successful_response_no_params(self, client: OpenF1Client) -> None:
        """Deve funcionar sem parâmetros de query."""
        expected = [{"driver_number": 44}]

        with patch("requests.get", return_value=_mock_response(200, expected)):
            result = client.get("drivers")

        assert result == expected

    def test_rate_limit_429_retries_and_succeeds(self, client: OpenF1Client) -> None:
        """Deve tentar novamente após receber HTTP 429 e retornar sucesso."""
        rate_limited = _mock_response(429)
        success = _mock_response(200, [{"lap_number": 1}])

        with patch("requests.get", side_effect=[rate_limited, success]) as mock_get:
            result = client.get("laps")

        assert result == [{"lap_number": 1}]
        assert mock_get.call_count == 2

    def test_rate_limit_429_exhausts_retries_raises(self, client: OpenF1Client) -> None:
        """Deve levantar HTTPError após esgotar todas as tentativas (429 persistente)."""
        rate_limited = _mock_response(429)

        # 3 retry_waits + 1 tentativa final que levanta = 4 chamadas
        with (
            patch("requests.get", return_value=rate_limited),
            pytest.raises(requests.HTTPError),
        ):
            client.get("laps")

    def test_429_retries_correct_number_of_times(self, client: OpenF1Client) -> None:
        """Deve tentar exatamente len(retry_waits) + 1 vezes antes de desistir."""
        rate_limited = _mock_response(429)

        with (
            patch("requests.get", return_value=rate_limited) as mock_get,
            pytest.raises(requests.HTTPError),
        ):
            client.get("laps")

        # retry_waits=[0,0,0] → 3 retries + 1 final = 4 chamadas
        assert mock_get.call_count == 4

    def test_http_500_raises_http_error(self, client: OpenF1Client) -> None:
        """Deve levantar HTTPError imediatamente para erros 5xx."""
        with (
            patch("requests.get", return_value=_mock_response(500)),
            pytest.raises(requests.HTTPError),
        ):
            client.get("laps")

    def test_http_404_raises_http_error(self, client: OpenF1Client) -> None:
        """Deve levantar HTTPError para 404 que não seja 'No results found'."""
        mock = MagicMock()
        mock.status_code = 404
        mock.json.return_value = {"detail": "Not found."}
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)

        with patch("requests.get", return_value=mock), pytest.raises(requests.HTTPError):
            client.get("sessions")

    def test_http_404_no_results_returns_empty_list(self, client: OpenF1Client) -> None:
        """Deve retornar lista vazia quando 404 indica 'No results found'.

        A API OpenF1 usa 404 para sinalizar ausência de dados (comportamento normal).
        """
        mock = MagicMock()
        mock.status_code = 404
        mock.json.return_value = {"detail": "No results found."}
        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)

        with patch("requests.get", return_value=mock):
            result = client.get("pit", params={"session_key": 9094})

        assert result == []

    def test_timeout_raises_timeout_error(self, client: OpenF1Client) -> None:
        """Deve propagar Timeout do requests."""
        with (
            patch("requests.get", side_effect=requests.Timeout),
            pytest.raises(requests.Timeout),
        ):
            client.get("drivers")


class TestOpenF1ClientInit:
    def test_default_base_url(self) -> None:
        """Deve usar a URL padrão da OpenF1 quando nenhuma for fornecida."""
        c = OpenF1Client()
        assert c.base_url == "https://api.openf1.org/v1"

    def test_custom_base_url_strips_trailing_slash(self) -> None:
        """Deve remover a barra final da URL base."""
        c = OpenF1Client(base_url="https://custom.api.com/v1/")
        assert c.base_url == "https://custom.api.com/v1"

    def test_default_retry_waits(self) -> None:
        """Deve usar os waits padrão de backoff."""
        c = OpenF1Client()
        assert c.retry_waits == [5.0, 15.0, 30.0]

    def test_custom_retry_waits(self) -> None:
        """Deve aceitar retry_waits customizados."""
        c = OpenF1Client(retry_waits=[1.0, 2.0])
        assert c.retry_waits == [1.0, 2.0]

    def test_throttle_waits_between_requests(self) -> None:
        """Deve aguardar min_interval entre requests consecutivos."""
        c = OpenF1Client(
            base_url="https://api.test.local/v1/",
            timeout=5,
            min_interval=0.1,
            retry_waits=[],
        )
        success = _mock_response(200, [{"ok": True}])

        with patch("requests.get", return_value=success):
            start = time.monotonic()
            c.get("laps")
            c.get("laps")  # segunda chamada deve esperar min_interval
            elapsed = time.monotonic() - start

        # Duas chamadas com min_interval=0.1 → pelo menos 0.09s de espera total
        assert elapsed >= 0.09
