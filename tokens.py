from dataclasses import dataclass

@dataclass
class Token:
    tipo: str
    valor: str
    linha: int 