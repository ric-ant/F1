"""Testes para o módulo fetcher.py."""

from unittest.mock import MagicMock

import pytest

from f1.fetcher import (
    TrackTopLaps,
    fetch_drivers,
    fetch_laps,
    fetch_race_sessions,
    fetch_season_top_laps,
    get_top_laps,
)
from f1.models import Driver, Lap, Session


@pytest.fixture()
def mock_client() -> MagicMock:
    """Retorna um mock do OpenF1Client."""
    return MagicMock()


# --- Dados de exemplo ---

SESSIONS_DATA = [
    {
        "session_key": 9222,
        "session_name": "Race",
        "date_start": "2023-05-28T13:00:00+00:00",
        "country_name": "Monaco",
        "meeting_key": 1208,
    },
    {
        "session_key": 9161,
        "session_name": "Race",
        "date_start": "2023-09-03T13:00:00+00:00",
        "country_name": "Italy",
        "meeting_key": 1219,
    },
]

DRIVERS_DATA = [
    {
        "driver_number": 1,
        "full_name": "Max Verstappen",
        "team_name": "Red Bull",
        "name_acronym": "VER",
    },
    {
        "driver_number": 44,
        "full_name": "Lewis Hamilton",
        "team_name": "Mercedes",
        "name_acronym": "HAM",
    },
]

LAPS_DATA = [
    {"driver_number": 1, "lap_number": 5, "lap_duration": 75.1},
    {"driver_number": 44, "lap_number": 3, "lap_duration": 74.5},
    {"driver_number": 1, "lap_number": 10, "lap_duration": 73.9},
    {"driver_number": 44, "lap_number": 15, "lap_duration": None},  # volta de pit
    {"driver_number": 1, "lap_number": 20, "lap_duration": 76.2},
    {"driver_number": 44, "lap_number": 25, "lap_duration": 74.1},
    {"driver_number": 1, "lap_number": 30, "lap_duration": 74.8},
]


class TestFetchRaceSessions:
    def test_returns_list_of_sessions(self, mock_client: MagicMock) -> None:
        """Deve retornar lista de Session para corridas do ano."""
        mock_client.get.return_value = SESSIONS_DATA

        sessions = fetch_race_sessions(mock_client, 2023)

        assert len(sessions) == 2
        assert all(isinstance(s, Session) for s in sessions)
        assert sessions[0].country_name == "Monaco"
        assert sessions[1].country_name == "Italy"

    def test_calls_api_with_correct_params(self, mock_client: MagicMock) -> None:
        """Deve chamar /sessions com year e session_name=Race."""
        mock_client.get.return_value = SESSIONS_DATA

        fetch_race_sessions(mock_client, 2023)

        mock_client.get.assert_called_once_with(
            "sessions", params={"year": 2023, "session_name": "Race"}
        )

    def test_raises_value_error_when_no_sessions(self, mock_client: MagicMock) -> None:
        """Deve levantar ValueError quando não houver corridas para o ano."""
        mock_client.get.return_value = []

        with pytest.raises(ValueError, match="Nenhuma sessão de corrida encontrada"):
            fetch_race_sessions(mock_client, 1990)


class TestFetchDrivers:
    def test_returns_list_of_drivers(self, mock_client: MagicMock) -> None:
        """Deve retornar lista de Driver corretamente."""
        mock_client.get.return_value = DRIVERS_DATA

        drivers = fetch_drivers(mock_client, 9222)

        assert len(drivers) == 2
        assert all(isinstance(d, Driver) for d in drivers)
        assert drivers[0].name_acronym == "VER"

    def test_returns_empty_when_no_drivers(self, mock_client: MagicMock) -> None:
        """Deve retornar lista vazia quando não há pilotos."""
        mock_client.get.return_value = []
        assert fetch_drivers(mock_client, 9999) == []


class TestFetchLaps:
    def test_returns_list_of_laps(self, mock_client: MagicMock) -> None:
        """Deve retornar lista de Lap corretamente."""
        mock_client.get.return_value = LAPS_DATA

        laps = fetch_laps(mock_client, 9222)

        assert len(laps) == 7
        assert all(isinstance(lap, Lap) for lap in laps)

    def test_calls_api_with_session_key(self, mock_client: MagicMock) -> None:
        """Deve chamar /laps com o session_key correto."""
        mock_client.get.return_value = []

        fetch_laps(mock_client, 9222)

        mock_client.get.assert_called_once_with("laps", params={"session_key": 9222})


class TestGetTopLaps:
    def _make_laps(self) -> list[Lap]:
        return [Lap.from_dict(d) for d in LAPS_DATA]

    def test_returns_top_n_fastest(self) -> None:
        """Deve retornar as N voltas mais rápidas."""
        laps = self._make_laps()
        top = get_top_laps(laps, top_n=3)

        assert len(top) == 3
        # Deve estar ordenado do mais rápido ao mais lento
        assert top[0].lap_duration == 73.9
        assert top[1].lap_duration == 74.1
        assert top[2].lap_duration == 74.5

    def test_excludes_none_duration(self) -> None:
        """Deve excluir voltas com lap_duration=None (voltas de pit)."""
        laps = self._make_laps()
        top = get_top_laps(laps, top_n=10)

        assert all(lap.lap_duration is not None for lap in top)
        # LAPS_DATA tem 7 entradas, mas 1 tem duration=None → máximo 6 válidas
        assert len(top) == 6

    def test_returns_less_than_top_n_if_insufficient_laps(self) -> None:
        """Deve retornar o que tiver se houver menos voltas válidas que top_n."""
        laps = [Lap.from_dict({"driver_number": 1, "lap_number": 1, "lap_duration": 90.0})]
        top = get_top_laps(laps, top_n=5)
        assert len(top) == 1

    def test_empty_laps_returns_empty(self) -> None:
        """Lista vazia retorna lista vazia."""
        assert get_top_laps([], top_n=5) == []

    def test_default_top_n_is_5(self) -> None:
        """O padrão deve ser top 5."""
        laps = [
            Lap.from_dict({"driver_number": 1, "lap_number": i, "lap_duration": float(90 + i)})
            for i in range(10)
        ]
        top = get_top_laps(laps)
        assert len(top) == 5


class TestFetchSeasonTopLaps:
    def _setup_client(self, mock_client: MagicMock) -> None:
        """Configura o mock para retornar dados de 2 corridas."""

        def side_effect(endpoint: str, params: dict | None = None) -> list:
            if endpoint == "sessions":
                return SESSIONS_DATA
            if endpoint == "drivers":
                return DRIVERS_DATA
            if endpoint == "laps":
                return LAPS_DATA
            return []

        mock_client.get.side_effect = side_effect

    def test_returns_list_of_track_top_laps(self, mock_client: MagicMock) -> None:
        """Deve retornar TrackTopLaps para cada corrida com dados."""
        self._setup_client(mock_client)

        result = fetch_season_top_laps(mock_client, 2023, top_n=3)

        assert len(result) == 2
        assert all(isinstance(r, TrackTopLaps) for r in result)

    def test_each_track_has_at_most_top_n_laps(self, mock_client: MagicMock) -> None:
        """Cada corrida deve ter no máximo top_n voltas."""
        self._setup_client(mock_client)

        result = fetch_season_top_laps(mock_client, 2023, top_n=3)

        for track in result:
            assert len(track.laps) <= 3

    def test_laps_are_sorted_fastest_first(self, mock_client: MagicMock) -> None:
        """As voltas de cada corrida devem estar ordenadas da mais rápida."""
        self._setup_client(mock_client)

        result = fetch_season_top_laps(mock_client, 2023, top_n=5)

        for track in result:
            durations = [lap.lap_duration for lap in track.laps]
            assert durations == sorted(durations)

    def test_no_pit_laps_in_results(self, mock_client: MagicMock) -> None:
        """Voltas de pit (lap_duration=None) não devem aparecer no resultado."""
        self._setup_client(mock_client)

        result = fetch_season_top_laps(mock_client, 2023, top_n=5)

        for track in result:
            assert all(lap.lap_duration is not None for lap in track.laps)

    def test_progress_callback_is_called(self, mock_client: MagicMock) -> None:
        """O callback de progresso deve ser chamado uma vez por corrida."""
        self._setup_client(mock_client)
        calls: list[tuple] = []

        fetch_season_top_laps(
            mock_client, 2023, top_n=3, progress_callback=lambda i, t, n: calls.append((i, t, n))
        )

        assert len(calls) == 2
        assert calls[0] == (1, 2, "Monaco")
        assert calls[1] == (2, 2, "Italy")

    def test_raises_value_error_for_invalid_year(self, mock_client: MagicMock) -> None:
        """Deve propagar ValueError de fetch_race_sessions."""
        mock_client.get.return_value = []

        with pytest.raises(ValueError, match="Nenhuma sessão"):
            fetch_season_top_laps(mock_client, 1990)

    def test_skips_session_with_no_laps(self, mock_client: MagicMock) -> None:
        """Corridas sem dados de voltas devem ser silenciosamente ignoradas."""

        def side_effect(endpoint: str, params: dict | None = None) -> list:
            if endpoint == "sessions":
                return SESSIONS_DATA
            if endpoint == "drivers":
                return DRIVERS_DATA
            if endpoint == "laps":
                return []  # sem voltas
            return []

        mock_client.get.side_effect = side_effect

        result = fetch_season_top_laps(mock_client, 2023, top_n=5)

        assert result == []
