import yaml

from pydantic import BaseModel
from typing import Optional

class Config(BaseModel):
    connection_uri: str
    rescue_target_lat: float
    rescue_target_lon: float
    rescue_target_tolerance: float
    debug_mode: Optional[bool] = False
    camera_src: str

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)