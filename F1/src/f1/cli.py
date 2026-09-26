"""Entrypoint de linha de comando — Top 5 voltas mais rápidas por pista."""

import argparse
import sys

from f1.client import OpenF1Client
from f1.fetcher import fetch_race_sessions, fetch_season_top_laps
from f1.report import generate_dashboard

# 8 pistas padrão selecionadas para o projeto
DEFAULT_TRACKS = [
    "Bahrain",
    "Monaco",
    "Italy",
    "Japan",
    "Brazil",
    "Australia",
    "Belgium",
    "Netherlands",
]


def _build_parser() -> argparse.ArgumentParser:
    """Cria e retorna o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="f1-dashboard",
        description=(
            "Gera um dashboard HTML com as 5 voltas mais rápidas "
            "de 8 pistas selecionadas de uma temporada da F1."
        ),
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Ano da temporada (ex.: 2023, 2024)",
    )
    parser.add_argument(
        "--tracks",
        type=str,
        nargs="+",
        default=None,
        metavar="PAIS",
        help=(
            "Lista de países/pistas a incluir (ex.: --tracks Monaco Italy Japan). "
            f"Padrão: {', '.join(DEFAULT_TRACKS)}"
        ),
    )
    parser.add_argument(
        "--list-tracks",
        action="store_true",
        help="Lista todas as pistas disponíveis para o ano informado e encerra.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Número de voltas por pista (padrão: 5)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="dashboard.html",
        help="Caminho do arquivo HTML de saída (padrão: dashboard.html)",
    )
    return parser


def main() -> None:
    """Entrypoint principal do CLI f1-dashboard."""
    parser = _build_parser()
    args = parser.parse_args()

    client = OpenF1Client()

    try:
        # Modo de listagem de pistas disponíveis
        if args.list_tracks:
            print(f"Buscando pistas disponíveis para {args.year}...")
            sessions = fetch_race_sessions(client, args.year)
            print(f"\nPistas disponíveis em {args.year} ({len(sessions)} corridas):")
            for s in sessions:
                print(f"  - {s.country_name}")
            return

        # Definir pistas a usar
        tracks_to_use = args.tracks if args.tracks else DEFAULT_TRACKS
        print(f"Buscando top {args.top} voltas de {len(tracks_to_use)} pistas em {args.year}:")
        for t in tracks_to_use:
            print(f"  - {t}")
        print()

        def progress(idx: int, total: int, name: str) -> None:
            print(f"  [{idx}/{total}] {name}...")

        tracks = fetch_season_top_laps(
            client,
            year=args.year,
            top_n=args.top,
            countries=tracks_to_use,
            progress_callback=progress,
        )

        if not tracks:
            print(f"Nenhuma corrida com dados de voltas encontrada para {args.year}.")
            sys.exit(1)

        print(f"\nGerando dashboard ({len(tracks)} corridas) em '{args.output}'...")
        generate_dashboard(year=args.year, tracks=tracks, output_path=args.output)

        print(f"Dashboard gerado: {args.output}")

    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"Erro inesperado: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
