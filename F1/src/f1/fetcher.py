"""Orquestrador de chamadas à API OpenF1.

Resolve o fluxo meetings → sessions → laps e retorna modelos tipados.
"""

from dataclasses import dataclass

from f1.client import OpenF1Client
from f1.models import Driver, Lap, Session


@dataclass
class TrackTopLaps:
    """Top N voltas mais rápidas de uma corrida específica.

    Attributes:
        session: Dados da sessão (corrida).
        laps: Lista com as top N voltas, ordenadas da mais rápida para a mais lenta.
        drivers: Mapa de driver_number → Driver para lookup de nomes.
    """

    session: Session
    laps: list[Lap]
    drivers: dict[int, Driver]


def fetch_race_sessions(client: OpenF1Client, year: int) -> list[Session]:
    """Busca todas as sessões de corrida (Race) de uma temporada.

    Args:
        client: Instância do OpenF1Client.
        year: Ano do campeonato (ex.: 2023).

    Returns:
        Lista de Sessions do tipo "Race" para o ano informado.

    Raises:
        ValueError: Se nenhuma corrida for encontrada para o ano.
    """
    data = client.get("sessions", params={"year": year, "session_name": "Race"})

    if not data:
        raise ValueError(
            f"Nenhuma sessão de corrida encontrada para {year}. "
            "Verifique se o ano está correto (dados disponíveis a partir de 2023)."
        )

    return [Session.from_dict(d) for d in data]


def fetch_drivers(client: OpenF1Client, session_key: int) -> list[Driver]:
    """Busca os pilotos participantes de uma sessão.

    Args:
        client: Instância do OpenF1Client.
        session_key: Chave da sessão.

    Returns:
        Lista de instâncias de Driver.
    """
    data = client.get("drivers", params={"session_key": session_key})
    return [Driver.from_dict(d) for d in data]


def fetch_laps(client: OpenF1Client, session_key: int) -> list[Lap]:
    """Busca todas as voltas registradas em uma sessão.

    Args:
        client: Instância do OpenF1Client.
        session_key: Chave da sessão.

    Returns:
        Lista de instâncias de Lap.
    """
    data = client.get("laps", params={"session_key": session_key})
    return [Lap.from_dict(d) for d in data]


def get_top_laps(laps: list[Lap], top_n: int = 5) -> list[Lap]:
    """Filtra e retorna as N voltas mais rápidas, excluindo voltas de pit.

    Voltas com lap_duration=None (voltas de entrada/saída do pit) são descartadas.
    O resultado é ordenado da volta mais rápida para a mais lenta.

    Args:
        laps: Lista de todas as voltas de uma sessão.
        top_n: Número de voltas a retornar. Padrão: 5.

    Returns:
        Lista com as top_n voltas mais rápidas (lap_duration não nulo).
    """
    valid = [lap for lap in laps if lap.lap_duration is not None]
    sorted_laps = sorted(valid, key=lambda lap: lap.lap_duration)  # type: ignore[arg-type]
    return sorted_laps[:top_n]


def fetch_season_top_laps(
    client: OpenF1Client,
    year: int,
    top_n: int = 5,
    countries: list[str] | None = None,
    progress_callback: object = None,
) -> list[TrackTopLaps]:
    """Busca as top N voltas mais rápidas de corridas selecionadas da temporada.

    Para cada corrida do ano informado (filtrada por países se fornecido):
    1. Busca os pilotos da sessão
    2. Busca todas as voltas
    3. Filtra as top N mais rápidas (sem voltas de pit)

    Corridas sem dados de voltas são silenciosamente ignoradas.

    Args:
        client: Instância do OpenF1Client.
        year: Ano do campeonato.
        top_n: Número de voltas por corrida. Padrão: 5.
        countries: Lista de nomes de países para filtrar (ex.: ["Monaco", "Italy"]).
            Se None, usa todas as corridas da temporada.
        progress_callback: Callable opcional que recebe (índice, total, session_name)
            para reportar progresso. Ex.: lambda i, t, n: print(f"{i}/{t} {n}")

    Returns:
        Lista de TrackTopLaps, uma por corrida com dados disponíveis,
        ordenada pela data de início da sessão.

    Raises:
        ValueError: Se nenhuma corrida for encontrada para o ano.
        ValueError: Se algum país da lista não for encontrado na temporada.
    """
    sessions = fetch_race_sessions(client, year)

    # Filtrar por países se fornecido
    if countries:
        countries_lower = [c.lower() for c in countries]
        available = {(s.country_name or "").lower(): s for s in sessions}

        not_found = [c for c in countries if c.lower() not in available]
        if not_found:
            available_names = sorted(s.country_name or "?" for s in sessions)
            raise ValueError(
                f"País(es) não encontrado(s) na temporada {year}: {', '.join(not_found)}.\n"
                f"Disponíveis: {', '.join(available_names)}"
            )

        sessions = [available[c] for c in countries_lower]

    results: list[TrackTopLaps] = []

    for idx, session in enumerate(sessions):
        if callable(progress_callback):
            progress_callback(idx + 1, len(sessions), session.country_name or "?")

        if session.session_key is None:
            continue

        drivers_list = fetch_drivers(client, session.session_key)
        driver_map = {d.driver_number: d for d in drivers_list if d.driver_number is not None}

        laps = fetch_laps(client, session.session_key)
        top = get_top_laps(laps, top_n=top_n)

        if not top:
            continue

        results.append(TrackTopLaps(session=session, laps=top, drivers=driver_map))

    return results
