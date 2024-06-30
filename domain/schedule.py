from dataclasses import dataclass


@dataclass
class Schedule:
    school_code: int
    id: str
    date: str  # YYYYMMDD
    title: str
    contents: str
