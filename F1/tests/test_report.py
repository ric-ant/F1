"""Testes para o módulo report.py."""

from pathlib import Path

import plotly.graph_objects as go

from f1.fetcher import TrackTopLaps
from f1.models import Driver, Lap, Session
from f1.report import (
    _build_top_laps_table,
    _format_lap_time,
    build_top_laps_chart,
    generate_dashboard,
)

# --- Helpers de dados sintéticos ---


def make_session(country: str = "Monaco", session_key: int = 9222) -> Session:
    return Session(
        session_key=session_key,
        session_name="Race",
        date_start="2023-05-28T13:00:00+00:00",
        country_name=country,
    )


def make_driver_map() -> dict[int, Driver]:
    return {
        1: Driver(
            driver_number=1,
            full_name="Max Verstappen",
            team_name="Red Bull",
            name_acronym="VER",
        ),
        44: Driver(
            driver_number=44,
            full_name="Lewis Hamilton",
            team_name="Mercedes",
            name_acronym="HAM",
        ),
    }


def make_top_laps(n: int = 5) -> list[Lap]:
    """Cria N voltas sintéticas já ordenadas do mais rápido ao mais lento."""
    base = 73.0
    return [
        Lap(
            driver_number=1 if i % 2 == 0 else 44,
            lap_number=i + 1,
            lap_duration=base + i * 0.3,
            duration_sector_1=20.0 + i * 0.1,
            duration_sector_2=25.0 + i * 0.1,
            duration_sector_3=28.0 + i * 0.1,
        )
        for i in range(n)
    ]


def make_track(country: str = "Monaco", session_key: int = 9222, n: int = 5) -> TrackTopLaps:
    return TrackTopLaps(
        session=make_session(country, session_key),
        laps=make_top_laps(n),
        drivers=make_driver_map(),
    )


# --- Testes ---


class TestFormatLapTime:
    def test_format_under_one_minute(self) -> None:
        """Tempos abaixo de 60s devem ser formatados como 0:SS.mmm."""
        assert _format_lap_time(59.123) == "0:59.123"

    def test_format_over_one_minute(self) -> None:
        """Tempos acima de 60s devem mostrar os minutos corretamente."""
        assert _format_lap_time(73.456) == "1:13.456"

    def test_format_exactly_one_minute(self) -> None:
        """60.0s deve ser exibido como 1:00.000."""
        assert _format_lap_time(60.0) == "1:00.000"


class TestBuildTopLapsChart:
    def test_returns_figure(self) -> None:
        """Deve retornar um go.Figure."""
        tracks = [make_track("Monaco"), make_track("Italy", 9161)]
        fig = build_top_laps_chart(tracks)
        assert isinstance(fig, go.Figure)

    def test_figure_has_correct_number_of_traces(self) -> None:
        """Deve ter um trace por posição no ranking (top 5 → 5 traces)."""
        tracks = [make_track("Monaco"), make_track("Italy", 9161)]
        fig = build_top_laps_chart(tracks)
        assert len(fig.data) == 5

    def test_traces_are_horizontal_bars(self) -> None:
        """Todos os traces devem ser barras horizontais."""
        tracks = [make_track()]
        fig = build_top_laps_chart(tracks)
        for trace in fig.data:
            assert isinstance(trace, go.Bar)
            assert trace.orientation == "h"

    def test_trace_names_indicate_ranking(self) -> None:
        """Os traces devem ser nomeados com a posição (1º lugar, 2º lugar, etc.)."""
        tracks = [make_track()]
        fig = build_top_laps_chart(tracks)
        names = [t.name for t in fig.data]
        assert "1º lugar" in names
        assert "5º lugar" in names

    def test_empty_tracks_returns_empty_figure(self) -> None:
        """Com lista vazia, deve retornar figura sem traces."""
        fig = build_top_laps_chart([])
        assert len(fig.data) == 0

    def test_tracks_with_fewer_laps(self) -> None:
        """Deve funcionar com corridas que têm menos de top_n voltas."""
        track = make_track(n=2)
        fig = build_top_laps_chart([track])
        assert len(fig.data) == 2


class TestBuildTopLapsTable:
    def test_returns_html_string(self) -> None:
        """Deve retornar uma string HTML."""
        tracks = [make_track()]
        html = _build_top_laps_table(tracks)
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_country_name(self) -> None:
        """A tabela deve conter o nome da pista."""
        tracks = [make_track("Monaco")]
        html = _build_top_laps_table(tracks)
        assert "Monaco" in html

    def test_contains_driver_acronym(self) -> None:
        """A tabela deve conter o acrônimo do piloto."""
        tracks = [make_track()]
        html = _build_top_laps_table(tracks)
        assert "VER" in html or "HAM" in html

    def test_empty_tracks_returns_no_data_message(self) -> None:
        """Com lista vazia deve retornar mensagem de sem dados."""
        html = _build_top_laps_table([])
        assert "Nenhum dado" in html


class TestGenerateDashboard:
    def test_creates_output_file(self, tmp_path: Path) -> None:
        """Deve criar o arquivo HTML no caminho especificado."""
        output = tmp_path / "test.html"
        generate_dashboard(2023, [make_track()], output_path=str(output))
        assert output.exists()

    def test_html_contains_year(self, tmp_path: Path) -> None:
        """O HTML deve conter o ano da temporada no título."""
        output = tmp_path / "test.html"
        generate_dashboard(2023, [make_track()], output_path=str(output))
        content = output.read_text(encoding="utf-8")
        assert "2023" in content

    def test_html_contains_plotly(self, tmp_path: Path) -> None:
        """O HTML deve incluir referência ao Plotly."""
        output = tmp_path / "test.html"
        generate_dashboard(2023, [make_track()], output_path=str(output))
        content = output.read_text(encoding="utf-8")
        assert "plotly" in content.lower()

    def test_html_contains_track_name(self, tmp_path: Path) -> None:
        """O HTML deve conter o nome da pista na tabela."""
        output = tmp_path / "test.html"
        generate_dashboard(2023, [make_track("Monaco")], output_path=str(output))
        content = output.read_text(encoding="utf-8")
        assert "Monaco" in content

    def test_html_valid_structure(self, tmp_path: Path) -> None:
        """O HTML gerado deve ter estrutura básica válida."""
        output = tmp_path / "test.html"
        generate_dashboard(2023, [make_track()], output_path=str(output))
        content = output.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content

    def test_html_mentions_race_count(self, tmp_path: Path) -> None:
        """O HTML deve mencionar o número de corridas analisadas."""
        output = tmp_path / "test.html"
        tracks = [make_track("Monaco"), make_track("Italy", 9161)]
        generate_dashboard(2023, tracks, output_path=str(output))
        content = output.read_text(encoding="utf-8")
        assert "2 corridas" in content

    def test_empty_tracks(self, tmp_path: Path) -> None:
        """Deve lidar com lista vazia de corridas sem erro."""
        output = tmp_path / "test.html"
        generate_dashboard(2023, [], output_path=str(output))
        assert output.exists()
