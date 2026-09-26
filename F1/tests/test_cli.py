"""Testes para o módulo cli.py."""

import sys
from unittest.mock import patch

import pytest

from f1.cli import _build_parser, main
from f1.fetcher import TrackTopLaps
from f1.models import Driver, Lap, Session

# --- Dados de exemplo ---

MOCK_DRIVER_MAP = {
    1: Driver(
        driver_number=1,
        full_name="Max Verstappen",
        team_name="Red Bull",
        name_acronym="VER",
    ),
}

MOCK_LAPS = [
    Lap(
        driver_number=1,
        lap_number=5,
        lap_duration=74.5,
        duration_sector_1=20.0,
        duration_sector_2=25.0,
        duration_sector_3=29.5,
    ),
]

MOCK_TRACKS = [
    TrackTopLaps(
        session=Session(
            session_key=9222,
            session_name="Race",
            date_start="2023-05-28T13:00:00+00:00",
            country_name="Monaco",
        ),
        laps=MOCK_LAPS,
        drivers=MOCK_DRIVER_MAP,
    ),
]


class TestBuildParser:
    def test_parses_required_year(self) -> None:
        """Deve parsear o argumento obrigatório --year."""
        parser = _build_parser()
        args = parser.parse_args(["--year", "2023"])
        assert args.year == 2023

    def test_default_top_is_5(self) -> None:
        """O padrão de --top deve ser 5."""
        parser = _build_parser()
        args = parser.parse_args(["--year", "2023"])
        assert args.top == 5

    def test_default_output_is_dashboard(self) -> None:
        """O padrão de --output deve ser 'dashboard.html'."""
        parser = _build_parser()
        args = parser.parse_args(["--year", "2023"])
        assert args.output == "dashboard.html"

    def test_parses_custom_top_and_output(self) -> None:
        """Deve aceitar --top e --output customizados."""
        parser = _build_parser()
        args = parser.parse_args(["--year", "2024", "--top", "3", "--output", "out.html"])
        assert args.top == 3
        assert args.output == "out.html"

    def test_year_is_int(self) -> None:
        """--year deve ser convertido para int."""
        parser = _build_parser()
        args = parser.parse_args(["--year", "2024"])
        assert isinstance(args.year, int)

    def test_no_gp_or_session_args(self) -> None:
        """O parser não deve ter os argumentos --gp nem --session."""
        parser = _build_parser()
        # Deve parsear sem erros sem --gp e --session
        args = parser.parse_args(["--year", "2023"])
        assert not hasattr(args, "gp")
        assert not hasattr(args, "session")


class TestMain:
    def test_main_calls_generate_dashboard(self) -> None:
        """main() deve chamar generate_dashboard com os parâmetros corretos."""
        argv = ["f1-dashboard", "--year", "2023", "--output", "test.html"]

        with (
            patch.object(sys, "argv", argv),
            patch("f1.cli.fetch_season_top_laps", return_value=MOCK_TRACKS) as mock_fetch,
            patch("f1.cli.generate_dashboard") as mock_gen,
        ):
            main()

        mock_fetch.assert_called_once()
        mock_gen.assert_called_once_with(year=2023, tracks=MOCK_TRACKS, output_path="test.html")

    def test_main_passes_year_and_top_to_fetcher(self) -> None:
        """main() deve passar year e top_n para fetch_season_top_laps."""
        argv = ["f1-dashboard", "--year", "2024", "--top", "3"]

        with (
            patch.object(sys, "argv", argv),
            patch("f1.cli.fetch_season_top_laps", return_value=MOCK_TRACKS) as mock_fetch,
            patch("f1.cli.generate_dashboard"),
        ):
            main()

        _, kwargs = mock_fetch.call_args
        assert kwargs["year"] == 2024
        assert kwargs["top_n"] == 3

    def test_main_exits_1_on_value_error(self) -> None:
        """main() deve chamar sys.exit(1) quando ValueError é levantado."""
        argv = ["f1-dashboard", "--year", "1990"]

        with (
            patch.object(sys, "argv", argv),
            patch("f1.cli.fetch_season_top_laps", side_effect=ValueError("Nenhuma sessão")),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1

    def test_main_exits_1_on_empty_tracks(self) -> None:
        """main() deve chamar sys.exit(1) quando não há corridas com dados."""
        argv = ["f1-dashboard", "--year", "2023"]

        with (
            patch.object(sys, "argv", argv),
            patch("f1.cli.fetch_season_top_laps", return_value=[]),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1

    def test_main_exits_1_on_generic_exception(self) -> None:
        """main() deve chamar sys.exit(1) para exceções genéricas."""
        argv = ["f1-dashboard", "--year", "2023"]

        with (
            patch.object(sys, "argv", argv),
            patch("f1.cli.fetch_season_top_laps", side_effect=ConnectionError("Falha")),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 1
