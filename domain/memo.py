from dataclasses import dataclass


@dataclass
class Memo:
    memo_id: str
    user_id: str
    date: str
    contents: str
