import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OracleConfig:
    user: str = os.getenv("ORACLE_USER", "travel_admin")
    password: str = os.getenv("ORACLE_PASSWORD", "travel_admin")
    dsn: str = os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1")


ORACLE_CONFIG = OracleConfig()
