"""Gerador de dashboard HTML — Top 5 voltas mais rápidas por pista."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from f1.fetcher import TrackTopLaps
from f1.models import Driver


def _format_lap_time(seconds: float) -> str:
    """Formata um tempo em segundos para o formato M:SS.mmm.

    Args:
        seconds: Tempo total em segundos.

    Returns:
        String no formato "1:23.456".
    """
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes}:{remaining:06.3f}"


def _driver_label(driver: Driver | None, driver_number: int | None) -> str:
    """Retorna o label do piloto (acrônimo ou número)."""
    if driver and driver.name_acronym:
        return driver.name_acronym
    return str(driver_number or "?")


def build_top_laps_chart(tracks: list[TrackTopLaps]) -> go.Figure:
    """Constrói o gráfico de barras com as top 5 voltas por pista.

    Gráfico de barras agrupadas: eixo X = tempo da volta (segundos),
    eixo Y = pista (país), uma barra por posição no ranking (1º ao 5º).
    Hover mostra piloto, equipe e tempo formatado.

    Args:
        tracks: Lista de TrackTopLaps com os dados de cada corrida.

    Returns:
        Figura Plotly com o gráfico de barras horizontais.
    """
    if not tracks:
        fig = go.Figure()
        fig.update_layout(title="Nenhum dado disponível")
        return fig

    top_n = max(len(t.laps) for t in tracks)

    # Cores para posições 1º a 5º
    colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#4A90D9", "#7ED321"]

    fig = make_subplots(rows=1, cols=1)

    for pos in range(top_n):
        x_vals: list[float] = []
        y_vals: list[str] = []
        hover_texts: list[str] = []

        for track in tracks:
            if pos >= len(track.laps):
                continue

            lap = track.laps[pos]
            country = track.session.country_name or "?"
            driver = track.drivers.get(lap.driver_number or -1)
            label = _driver_label(driver, lap.driver_number)
            team = driver.team_name if driver and driver.team_name else "—"
            duration = lap.lap_duration or 0.0
            formatted = _format_lap_time(duration)

            s1 = f"{lap.duration_sector_1:.3f}s" if lap.duration_sector_1 else "—"
            s2 = f"{lap.duration_sector_2:.3f}s" if lap.duration_sector_2 else "—"
            s3 = f"{lap.duration_sector_3:.3f}s" if lap.duration_sector_3 else "—"

            x_vals.append(duration)
            y_vals.append(country)
            hover_texts.append(
                f"<b>{label}</b> — {team}<br>"
                f"Tempo: {formatted}<br>"
                f"Volta: {lap.lap_number}<br>"
                f"S1: {s1} | S2: {s2} | S3: {s3}"
            )

        if not x_vals:
            continue

        color = colors[pos] if pos < len(colors) else "#999999"
        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=y_vals,
                orientation="h",
                name=f"{pos + 1}º lugar",
                marker_color=color,
                text=[_format_lap_time(v) for v in x_vals],
                textposition="inside",
                hovertext=hover_texts,
                hoverinfo="text",
            )
        )

    fig.update_layout(
        barmode="group",
        title="Top 5 Voltas Mais Rápidas por Pista",
        xaxis_title="Tempo da Volta (s)",
        yaxis_title="",
        yaxis={"autorange": "reversed"},
        legend_title="Ranking",
        template="plotly_white",
        height=max(400, len(tracks) * 60),
        margin={"l": 120},
    )

    return fig


def _build_top_laps_table(tracks: list[TrackTopLaps]) -> str:
    """Constrói tabela HTML com o detalhamento das top 5 voltas de cada pista.

    Args:
        tracks: Lista de TrackTopLaps.

    Returns:
        String HTML com a tabela completa.
    """
    if not tracks:
        return "<p>Nenhum dado disponível.</p>"

    rows = ""
    for track in tracks:
        country = track.session.country_name or "?"
        date = (track.session.date_start or "")[:10]  # só a data, sem hora

        for pos, lap in enumerate(track.laps):
            driver = track.drivers.get(lap.driver_number or -1)
            label = _driver_label(driver, lap.driver_number)
            team = driver.team_name if driver and driver.team_name else "—"
            duration = lap.lap_duration or 0.0
            formatted = _format_lap_time(duration)
            s1 = f"{lap.duration_sector_1:.3f}" if lap.duration_sector_1 else "—"
            s2 = f"{lap.duration_sector_2:.3f}" if lap.duration_sector_2 else "—"
            s3 = f"{lap.duration_sector_3:.3f}" if lap.duration_sector_3 else "—"
            bg = "#fff9e6" if pos == 0 else "white"

            rows += (
                f'  <tr style="background-color:{bg}">'
                f"<td>{country}</td>"
                f"<td>{date}</td>"
                f"<td><b>{pos + 1}º</b></td>"
                f"<td>{label}</td>"
                f"<td>{team}</td>"
                f"<td><b>{formatted}</b></td>"
                f"<td>{lap.lap_number}</td>"
                f"<td>{s1}</td><td>{s2}</td><td>{s3}</td>"
                f"</tr>\n"
            )

    return f"""
<table border="1" cellpadding="6" cellspacing="0"
       style="border-collapse:collapse; font-family:sans-serif; font-size:13px; width:100%;">
  <thead style="background-color:#e10600; color:white; position:sticky; top:0;">
    <tr>
      <th>Pista</th>
      <th>Data</th>
      <th>Pos.</th>
      <th>Piloto</th>
      <th>Equipe</th>
      <th>Tempo</th>
      <th>Volta</th>
      <th>S1 (s)</th>
      <th>S2 (s)</th>
      <th>S3 (s)</th>
    </tr>
  </thead>
  <tbody>
{rows}  </tbody>
</table>
"""


def generate_dashboard(
    year: int,
    tracks: list[TrackTopLaps],
    output_path: str = "dashboard.html",
) -> None:
    """Gera o dashboard HTML com as top 5 voltas por pista da temporada.

    O arquivo HTML contém:
    - Título com o ano da temporada
    - Gráfico de barras horizontais com o ranking por pista (Plotly via CDN)
    - Tabela detalhada com piloto, equipe, tempo e setores

    Args:
        year: Ano da temporada exibida.
        tracks: Lista de TrackTopLaps com dados de cada corrida.
        output_path: Caminho do arquivo HTML de saída.
    """
    title = f"F1 {year} — Top 5 Voltas Mais Rápidas por Pista"
    n_tracks = len(tracks)

    fig = build_top_laps_chart(tracks)
    chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    table_html = _build_top_laps_table(tracks)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: sans-serif;
      margin: 0;
      padding: 20px 40px;
      background-color: #f5f5f5;
    }}
    h1 {{
      color: #e10600;
      border-bottom: 3px solid #e10600;
      padding-bottom: 8px;
    }}
    h2 {{
      color: #333;
      margin-top: 40px;
    }}
    .subtitle {{
      color: #666;
      font-size: 15px;
      margin-top: -10px;
      margin-bottom: 20px;
    }}
    .card {{
      background: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 40px;
    }}
    .table-wrapper {{
      overflow-x: auto;
    }}
    td, th {{
      white-space: nowrap;
    }}
  </style>
</head>
<body>
  <h1>🏎️ {title}</h1>
  <p class="subtitle">{n_tracks} corridas analisadas · Voltas de pit stop excluídas</p>

  <div class="card">
    <h2>Ranking por Pista</h2>
    {chart_html}
  </div>

  <div class="card">
    <h2>Detalhamento — Top 5 por Corrida</h2>
    <div class="table-wrapper">
      {table_html}
    </div>
  </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
