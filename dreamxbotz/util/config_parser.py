# Simple config parser without external dependencies
from os import environ
from typing import Dict, Optional


class TokenParser:
    def __init__(self, config_file: Optional[str] = None):
        self.tokens = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        self.tokens = {}
        # Just return empty dict since we don't need multi-token anymore
        return self.tokens
