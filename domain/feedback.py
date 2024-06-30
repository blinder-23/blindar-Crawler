from dataclasses import dataclass


@dataclass
class Feedback:
    user_id: str
    device_name: str
    os_version: str
    app_version: str
    contents: str
