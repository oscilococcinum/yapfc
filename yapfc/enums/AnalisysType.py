from enum import Enum, StrEnum

class AnalisysType(StrEnum):
    Elastic = '*ELASTIC'
    ElastoPlastic = '*PLASTIC'
    Hyperelastic = '*HYPERELASTIC'