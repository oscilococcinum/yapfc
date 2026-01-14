from enum import Enum, auto


class SelectionCategory(Enum):
    Elements = 0
    Nodes = 1
    Edges = 2
    Surfaces = 3
    Volumes = 4