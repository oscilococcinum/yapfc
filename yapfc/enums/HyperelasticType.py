from enum import Enum, StrEnum


class HyperelasticType(StrEnum):
    ArrudaBoyce = 'ARRUDA-BOYCE'
    MooneyRivlin = 'MOONEY-RIVLIN'
    NeoHooke = 'NEO HOOKE'
    Ogden = 'OGDEN'
    Polynomial = 'POLYNOMIAL'
    ReducedPolynomial = 'REDUCED POLYNOMIAL'
    Yeoh = 'YEOH'
    Hyperfoam = 'HYPERFOAM'
