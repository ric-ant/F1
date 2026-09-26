"""HTTP client para a API OpenF1 com throttle e retry com backoff."""

import time

import requests

# Limites do tier gratuito da OpenF1: 3 req/s e 30/min.
# Espaçamento mínimo entre requisições para não ultrapassar 3 req/s.
_MIN_INTERVAL = 0.35  # segundos entre requests (~2.8 req/s, margem de segurança)

# Tempos de espera para retry em caso de 429 (backoff exponencial)
_RETRY_WAITS = [5.0, 15.0, 30.0]  # 3 tentativas: 5s, 15s, 30s


class OpenF1Client:
    """Cliente HTTP para a API OpenF1.

    Aplica throttle automático entre requests (~2.8 req/s) para respeitar
    o rate limit do tier gratuito (3 req/s / 30 req/min), e faz retry com
    backoff exponencial em caso de HTTP 429.

    Args:
        base_url: URL base da API. Padrão: https://api.openf1.org/v1/
        timeout: Timeout em segundos para cada requisição. Padrão: 30.
        min_interval: Intervalo mínimo entre requests em segundos. Padrão: 0.35.
        retry_waits: Lista de tempos de espera (s) para cada tentativa de retry.
    """

    DEFAULT_BASE_URL = "https://api.openf1.org/v1/"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        min_interval: float = _MIN_INTERVAL,
        retry_waits: list[float] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_interval = min_interval
        self.retry_waits = retry_waits if retry_waits is not None else list(_RETRY_WAITS)
        self._last_request_time: float = 0.0

    def _throttle(self) -> None:
        """Aplica espera se necessário para respeitar o intervalo mínimo entre requests."""
        elapsed = time.monotonic() - self._last_request_time
        wait = self.min_interval - elapsed
        if wait > 0:
            time.sleep(wait)

    def get(self, endpoint: str, params: dict | None = None) -> list[dict]:
        """Faz uma requisição GET ao endpoint informado.

        Aplica throttle automático antes de cada request. Em caso de HTTP 429
        (rate limit), aguarda com backoff crescente e tenta novamente.

        A API OpenF1 retorna HTTP 404 com body {"detail": "No results found."}
        quando não existem dados para os filtros aplicados (comportamento normal).
        Nesses casos, retorna lista vazia em vez de levantar exceção.

        Args:
            endpoint: Caminho do endpoint (ex.: "laps", "drivers").
            params: Parâmetros de query string (filtros da API).

        Returns:
            Lista de dicts com os dados retornados pela API.
            Lista vazia se a API retornar 404 "No results found".

        Raises:
            requests.HTTPError: Para erros HTTP que não sejam 429 nem
                404-sem-resultados.
            requests.Timeout: Se a requisição exceder o timeout configurado.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for _attempt, wait_after in enumerate([*self.retry_waits, None]):
            self._throttle()
            self._last_request_time = time.monotonic()

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 429:
                if wait_after is not None:
                    time.sleep(wait_after)
                    continue
                # Esgotou todas as tentativas
                response.raise_for_status()

            # 404 "No results found" é comportamento normal da API (sem dados)
            if response.status_code == 404:
                try:
                    body = response.json()
                    if isinstance(body, dict) and "no results" in body.get("detail", "").lower():
                        return []
                except Exception:  # noqa: BLE001
                    pass
                response.raise_for_status()

            response.raise_for_status()
            return response.json()

        return []  # pragma: no cover
