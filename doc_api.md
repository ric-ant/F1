# OpenF1 API — Resumo da Documentação

> Fonte: https://openf1.org/docs#api-endpoints
> API REST open-source com dados de telemetria, timing e sessões da Fórmula 1 (em tempo real e histórico).

## Visão geral

- **Base URL:** `https://api.openf1.org/v1/`
- **Formatos de resposta:** JSON (padrão) ou CSV (`?csv=true`)
- **Dados históricos** (a partir de 2023): gratuitos, sem autenticação
- **Dados em tempo real (live)**: requerem assinatura paga (autenticação via OAuth2, endpoint `POST /token`, com acesso também via MQTT/WebSocket)
- **Limites (tier gratuito):** 3 requisições/s e 30/min. Patrocinadores têm o dobro, além de conexões MQTT/WebSocket.
- Pode ser consultada direto do navegador ou de qualquer cliente HTTP.

## Autenticação (dados live)

```bash
curl -X POST "https://api.openf1.org/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=SEU_USUARIO&password=SUA_SENHA"
```
O token retornado é usado como `Authorization: Bearer <token>` nas chamadas.

## Filtragem de dados

Filtros são passados como query params, comparando qualquer atributo (exceto arrays), com operadores `=`, `>`, `>=`, `<`, `<=`.

```
https://api.openf1.org/v1/laps?session_key=9222&driver_number=55&is_pit_out_lap=true&lap_duration>=120
```

**Filtro por data/hora** (formatos flexíveis, compatíveis com `dateutil.parser`):
```
https://api.openf1.org/v1/sessions?date_start>=2023-09-01&date_end<=2023-09-30
```

## Formato CSV

Basta adicionar `csv=true` na URL:
```
https://api.openf1.org/v1/sessions?year=2023&csv=true
```

---

## Endpoints (18 no total)

| Endpoint | Descrição | Parâmetros/chave típicos |
|---|---|---|
| `GET /car_data` | Telemetria do carro (~3.7 Hz): freio, acelerador, marcha, RPM, velocidade, DRS | `driver_number`, `session_key`, `speed` |
| `GET /championship_drivers` *(beta)* | Classificação do campeonato de pilotos (só em sessões de corrida) | `session_key`, `driver_number` |
| `GET /championship_teams` *(beta)* | Classificação do campeonato de construtores | `session_key`, `team_name` |
| `GET /drivers` | Informações dos pilotos em uma sessão (nome, equipe, número, foto) | `driver_number`, `session_key` |
| `GET /intervals` | Intervalo entre pilotos e gap para o líder (só em corridas, atualiza ~4s) | `session_key`, `interval` |
| `GET /laps` | Detalhes por volta: setores, velocidades, duração | `session_key`, `driver_number`, `lap_number` |
| `GET /location` | Posição aproximada (x,y,z) do carro na pista (~3.7 Hz) | `session_key`, `driver_number`, `date` |
| `GET /meetings` | Informações do "Grande Prêmio"/fim de semana (várias sessões) | `year`, `country_name` |
| `GET /overtakes` | Ultrapassagens (inclui as por pit stop/penalidade), só em corridas | `session_key`, `overtaking_driver_number`, `overtaken_driver_number` |
| `GET /pit` | Passagens pelo pit lane (duração no box, na pista) | `session_key`, `stop_duration` |
| `GET /position` | Posição do piloto ao longo da sessão | `meeting_key`, `driver_number`, `position` |
| `GET /race_control` | Bandeiras, safety car, status da sessão, incidentes | `flag`, `driver_number`, `date` |
| `GET /sessions` | Informações de sessões (treino, classificação, corrida etc.) | `country_name`, `session_name`, `year` |
| `GET /session_result` | Resultado/classificação final da sessão | `session_key`, `position` |
| `GET /starting_grid` | Grid de largada da próxima corrida | `session_key`, `position` |
| `GET /stints` | Stints (períodos com o mesmo pneu) | `session_key`, `tyre_age_at_start` |
| `GET /team_radio` | Gravações de rádio piloto-equipe (cobertura parcial, reduzida desde 2026) | `session_key`, `driver_number` |
| `GET /weather` | Clima na pista, atualizado a cada minuto | `meeting_key`, `wind_direction`, `track_temperature` |

### Exemplo de chamada (Laps)
```bash
curl "https://api.openf1.org/v1/laps?session_key=9161&driver_number=63&lap_number=8"
```
```json
[
  {
    "date_start": "2023-09-16T13:59:07.606000+00:00",
    "driver_number": 63,
    "duration_sector_1": 26.966,
    "lap_duration": 91.743,
    "lap_number": 8,
    "session_key": 9161
  }
]
```

### Chaves de referência comuns (presentes na maioria dos endpoints)
- `meeting_key`: identifica o fim de semana de corrida (use `latest` para o atual)
- `session_key`: identifica a sessão específica (use `latest` para a atual)
- `driver_number`: número do piloto na temporada

---

## Tutoriais e suporte

- Tutoriais oficiais linkados na doc (ex.: dashboard de estratégia em Python, streaming de dados live)
- Suporte via [GitHub Discussions](https://github.com/br-g/openf1/discussions) e [issues](https://github.com/br-g/openf1/issues)
- Repositório: https://github.com/br-g/openf1

## Aviso legal
OpenF1 é um projeto independente, não afiliado oficialmente à Fórmula 1/FIA. Uso destinado a fins educacionais, pessoais e não comerciais.