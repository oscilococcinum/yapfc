from typing import TYPE_CHECKING
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor, vtkCellPicker, vtkPointPicker,
    vtkDataSetMapper
)
from yapfc.enums.SelectionCategory import SelectionCategory
from yapfc.util import timeit
if TYPE_CHECKING:
    from yapfc.Viewer import vtkViewer

class MouseInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self, parent:'vtkViewer'):
        self.AddObserver('LeftButtonPressEvent', self.left_button_press_event) #type:ignore
        self.parent: vtkViewer = parent
        self.selected_mapper = vtkDataSetMapper()
        self.selected_actor = vtkActor()

    def left_button_press_event(self, obj, event):
        match self.parent.selectionFilter:
            case SelectionCategory.Elements:
                self.pickCell()
            case SelectionCategory.Nodes:
                self.nodePick()
            case SelectionCategory.Edges:
                self.edgePick()
            case SelectionCategory.Surfaces:
               self.surfacePick() 
            case SelectionCategory.Volumes:
                self.volumePick()
        self.OnLeftButtonDown()

    def pickCell(self) -> None:
        pos = self.GetInteractor().GetEventPosition()

        picker = vtkCellPicker()
        picker.SetTolerance(0.005)

        picker.Pick(pos[0], pos[1], 0, self.parent.renderer)

        world_position = picker.GetPickPosition()

        cellId:int = picker.GetCellId()

        if cellId != -1:
            print(f'''Pick position is: ({world_position[0]:.6g}, {world_position[1]:.6g}, {world_position[2]:.6g})''')
            print(f'Cell id is: {cellId}')
            self.parent.changeInSelection(cellId, SelectionCategory.Elements)
        else:
            self.parent.changeInSelection(cellId, SelectionCategory.Elements)
            print('Selection clean')

    def nodePick(self) -> None:
        pos = self.GetInteractor().GetEventPosition()

        picker = vtkPointPicker()
        picker.SetTolerance(0.005)

        picker.Pick(pos[0], pos[1], 0, self.parent.renderer)

        world_position = picker.GetPickPosition()

        pointId:int = picker.GetPointId()

        if pointId != -1:
            print(f'''Pick position is: ({world_position[0]:.6g}, {world_position[1]:.6g}, {world_position[2]:.6g})''')
            print(f'Point id is: {pointId}')
            self.parent.changeInSelection(pointId, SelectionCategory.Nodes)
        else:
            self.parent.changeInSelection(pointId, SelectionCategory.Nodes)
            print('Selection clean')

    def edgePick(self) -> None:
        pass

    def surfacePick(self) -> None:
        pass

    def volumePick(self) -> None:
        pass