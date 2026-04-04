from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Weather:
    id: int
    name: str
    description: str
    icon_id: str


@dataclass
class Forecast:
    timestamp: datetime
    weather: list[Weather]

    clouds: int
    dew_point: float

    sunrise: datetime | None = None
    sunset: datetime | None = None


@dataclass
class Alert:
    sender_name: str
    event: str
    start: datetime
    end: datetime
    description: str


@dataclass
class ForecastPack:
    lat: float
    lon: float
    timezone: str
    timezone_offset: int

    current: Forecast | None = None
    minutely: list[Forecast] = field(default_factory=list)
    hourly: list[Forecast] = field(default_factory=list)
    daily: list[Forecast] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
