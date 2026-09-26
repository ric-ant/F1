"""Testes para o módulo models.py."""

from f1.models import Driver, Lap, Pit, Session, Stint


class TestSession:
    def test_from_dict_complete(self) -> None:
        """Deve criar Session corretamente a partir de dict completo."""
        data = {
            "session_key": 9222,
            "session_name": "Race",
            "date_start": "2023-05-28T13:00:00+00:00",
            "country_name": "Monaco",
        }
        session = Session.from_dict(data)
        assert session.session_key == 9222
        assert session.session_name == "Race"
        assert session.date_start == "2023-05-28T13:00:00+00:00"
        assert session.country_name == "Monaco"

    def test_from_dict_missing_fields(self) -> None:
        """Campos ausentes devem resultar em None, sem exceção."""
        session = Session.from_dict({})
        assert session.session_key is None
        assert session.session_name is None
        assert session.date_start is None
        assert session.country_name is None

    def test_from_dict_partial(self) -> None:
        """Deve aceitar dict com apenas alguns campos preenchidos."""
        session = Session.from_dict({"session_key": 100})
        assert session.session_key == 100
        assert session.session_name is None


class TestDriver:
    def test_from_dict_complete(self) -> None:
        """Deve criar Driver corretamente a partir de dict completo."""
        data = {
            "driver_number": 44,
            "full_name": "Lewis Hamilton",
            "team_name": "Mercedes",
            "name_acronym": "HAM",
        }
        driver = Driver.from_dict(data)
        assert driver.driver_number == 44
        assert driver.full_name == "Lewis Hamilton"
        assert driver.team_name == "Mercedes"
        assert driver.name_acronym == "HAM"

    def test_from_dict_missing_fields(self) -> None:
        """Campos ausentes devem resultar em None."""
        driver = Driver.from_dict({})
        assert driver.driver_number is None
        assert driver.full_name is None
        assert driver.team_name is None
        assert driver.name_acronym is None


class TestLap:
    def test_from_dict_complete(self) -> None:
        """Deve criar Lap corretamente com todos os campos."""
        data = {
            "driver_number": 1,
            "lap_number": 5,
            "lap_duration": 91.743,
            "duration_sector_1": 26.966,
            "duration_sector_2": 34.512,
            "duration_sector_3": 30.265,
        }
        lap = Lap.from_dict(data)
        assert lap.driver_number == 1
        assert lap.lap_number == 5
        assert lap.lap_duration == 91.743
        assert lap.duration_sector_1 == 26.966
        assert lap.duration_sector_2 == 34.512
        assert lap.duration_sector_3 == 30.265

    def test_from_dict_none_lap_duration(self) -> None:
        """lap_duration pode ser None (volta de pit)."""
        data = {"driver_number": 33, "lap_number": 10, "lap_duration": None}
        lap = Lap.from_dict(data)
        assert lap.lap_duration is None

    def test_from_dict_missing_fields(self) -> None:
        """Campos ausentes devem resultar em None."""
        lap = Lap.from_dict({})
        assert lap.driver_number is None
        assert lap.lap_number is None
        assert lap.lap_duration is None
        assert lap.duration_sector_1 is None
        assert lap.duration_sector_2 is None
        assert lap.duration_sector_3 is None


class TestStint:
    def test_from_dict_complete(self) -> None:
        """Deve criar Stint corretamente com todos os campos."""
        data = {
            "driver_number": 16,
            "lap_start": 1,
            "lap_end": 25,
            "compound": "SOFT",
            "tyre_age_at_start": 0,
        }
        stint = Stint.from_dict(data)
        assert stint.driver_number == 16
        assert stint.lap_start == 1
        assert stint.lap_end == 25
        assert stint.compound == "SOFT"
        assert stint.tyre_age_at_start == 0

    def test_from_dict_missing_fields(self) -> None:
        """Campos ausentes devem resultar em None."""
        stint = Stint.from_dict({})
        assert stint.driver_number is None
        assert stint.compound is None


class TestPit:
    def test_from_dict_complete(self) -> None:
        """Deve criar Pit corretamente com todos os campos."""
        data = {
            "driver_number": 55,
            "lap_number": 20,
            "pit_duration": 23.456,
        }
        pit = Pit.from_dict(data)
        assert pit.driver_number == 55
        assert pit.lap_number == 20
        assert pit.pit_duration == 23.456

    def test_from_dict_none_duration(self) -> None:
        """pit_duration pode ser None."""
        pit = Pit.from_dict({"driver_number": 11, "lap_number": 5, "pit_duration": None})
        assert pit.pit_duration is None

    def test_from_dict_missing_fields(self) -> None:
        """Campos ausentes devem resultar em None."""
        pit = Pit.from_dict({})
        assert pit.driver_number is None
        assert pit.lap_number is None
        assert pit.pit_duration is None
