from enum import Enum, auto


class CCXWriterCategory(Enum):
    MeshSubWriter = auto()
    MaterialSubWriter = auto()
    SectionSubWriter = auto()
    ConstraintSubWriter = auto()
    ContactSubWriter = auto()
    AmplitudeSubWriter = auto()
    InitialConditionSubWriter = auto()
    StepSubWriter = auto()
    BoundarySubWriter = auto()
    AnalysisSubWriter = auto()