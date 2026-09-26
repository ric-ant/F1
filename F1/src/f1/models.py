"""Dataclasses tipadas que representam as entidades retornadas pela API OpenF1."""

from dataclasses import dataclass


@dataclass
class Session:
    """Representa uma sessão de F1 (treino, qualificação, corrida etc.).

    Attributes:
        session_key: Identificador único da sessão.
        session_name: Nome da sessão (ex.: "Race", "Qualifying").
        date_start: Data/hora de início da sessão (ISO 8601).
        country_name: Nome do país onde ocorreu a sessão.
    """

    session_key: int | None
    session_name: str | None
    date_start: str | None
    country_name: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Cria uma instância de Session a partir de um dict da API.

        Campos ausentes resultam em None (sem levantar exceção).
        """
        return cls(
            session_key=data.get("session_key"),
            session_name=data.get("session_name"),
            date_start=data.get("date_start"),
            country_name=data.get("country_name"),
        )


@dataclass
class Driver:
    """Representa um piloto em uma sessão.

    Attributes:
        driver_number: Número do piloto na temporada.
        full_name: Nome completo do piloto.
        team_name: Nome da equipe.
        name_acronym: Acrônimo de 3 letras (ex.: "HAM", "VER").
    """

    driver_number: int | None
    full_name: str | None
    team_name: str | None
    name_acronym: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "Driver":
        """Cria uma instância de Driver a partir de um dict da API."""
        return cls(
            driver_number=data.get("driver_number"),
            full_name=data.get("full_name"),
            team_name=data.get("team_name"),
            name_acronym=data.get("name_acronym"),
        )


@dataclass
class Lap:
    """Representa uma volta registrada na sessão.

    Attributes:
        driver_number: Número do piloto.
        lap_number: Número da volta.
        lap_duration: Duração total da volta em segundos. None em voltas de pit.
        duration_sector_1: Duração do setor 1 em segundos.
        duration_sector_2: Duração do setor 2 em segundos.
        duration_sector_3: Duração do setor 3 em segundos.
    """

    driver_number: int | None
    lap_number: int | None
    lap_duration: float | None
    duration_sector_1: float | None
    duration_sector_2: float | None
    duration_sector_3: float | None

    @classmethod
    def from_dict(cls, data: dict) -> "Lap":
        """Cria uma instância de Lap a partir de um dict da API."""
        return cls(
            driver_number=data.get("driver_number"),
            lap_number=data.get("lap_number"),
            lap_duration=data.get("lap_duration"),
            duration_sector_1=data.get("duration_sector_1"),
            duration_sector_2=data.get("duration_sector_2"),
            duration_sector_3=data.get("duration_sector_3"),
        )


@dataclass
class Stint:
    """Representa um stint (período com o mesmo conjunto de pneus).

    Attributes:
        driver_number: Número do piloto.
        lap_start: Volta de início do stint.
        lap_end: Volta de fim do stint.
        compound: Composto do pneu (ex.: "SOFT", "MEDIUM", "HARD").
        tyre_age_at_start: Idade do pneu em voltas no início do stint.
    """

    driver_number: int | None
    lap_start: int | None
    lap_end: int | None
    compound: str | None
    tyre_age_at_start: int | None

    @classmethod
    def from_dict(cls, data: dict) -> "Stint":
        """Cria uma instância de Stint a partir de um dict da API."""
        return cls(
            driver_number=data.get("driver_number"),
            lap_start=data.get("lap_start"),
            lap_end=data.get("lap_end"),
            compound=data.get("compound"),
            tyre_age_at_start=data.get("tyre_age_at_start"),
        )


@dataclass
class Pit:
    """Representa um pit stop realizado durante a sessão.

    Attributes:
        driver_number: Número do piloto.
        lap_number: Volta em que ocorreu o pit stop.
        pit_duration: Duração da parada em segundos. Pode ser None.
    """

    driver_number: int | None
    lap_number: int | None
    pit_duration: float | None

    @classmethod
    def from_dict(cls, data: dict) -> "Pit":
        """Cria uma instância de Pit a partir de um dict da API."""
        return cls(
            driver_number=data.get("driver_number"),
            lap_number=data.get("lap_number"),
            pit_duration=data.get("pit_duration"),
        )
