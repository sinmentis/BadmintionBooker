import datetime
from dataclasses import dataclass
from enum import Enum


class TimeSlotStatus(Enum):
    # <div class="style_booked">Booked</div>
    Booked = "152, 251, 152"
    Peak = ""
    Pending = "227, 210, 228"
    Unavailable = "237, 228, 201"

    # <div>Available</div>
    Available = "247, 247, 247", "255, 255, 255"


@dataclass
class TimeSlot:
    time: datetime
    status: TimeSlotStatus


@dataclass
class Preference:
    week: int
    duration_min: int
    start_time: int
    court: int
    priority: int


@dataclass
class Config:
    url_login: str
    url_main: str
    username: str
    password: str
    preference: list
