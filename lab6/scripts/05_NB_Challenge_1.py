import vtk

rectGridReader = vtk.vtkRectilinearGridReader()
rectGridReader.SetFileName("D:/Notebooks_Bogota2017/SS_2017/data/jet4_0.500.vtk")
rectGridReader.Update()

#------------ CHALLENGE ONE ----------------------
rectGridOutline = vtk.vtkRectilinearGridOutlineFilter()
rectGridOutline.SetInputData(rectGridReader.GetOutput())

rectGridGeom = vtk.vtkRectilinearGridGeometryFilter()
rectGridGeom.SetInputData(rectGridReader.GetOutput())
rectGridGeom.SetExtent(0, 128, 0, 0, 0, 128) 

rectGridOutlineMapper = vtk.vtkPolyDataMapper()
rectGridOutlineMapper.SetInputConnection(rectGridOutline.GetOutputPort())

rectGridGeomMapper = vtk.vtkPolyDataMapper()
rectGridGeomMapper.SetInputConnection(rectGridGeom.GetOutputPort())

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(rectGridOutlineMapper)
outlineActor.GetProperty().SetColor(0, 0, 0)

gridGeomActor = vtk.vtkActor()
gridGeomActor.SetMapper(rectGridGeomMapper)
gridGeomActor.GetProperty().SetRepresentationToWireframe()
gridGeomActor.GetProperty().SetColor(1, 0, 0)

#------------ CHALLENGE TWO ----------------------
magnitudeCalcFilter = vtk.vtkArrayCalculator()
magnitudeCalcFilter.SetInputConnection(rectGridReader.GetOutputPort())
magnitudeCalcFilter.AddVectorArrayName('vectors')
magnitudeCalcFilter.SetResultArrayName('magnitude')
magnitudeCalcFilter.SetFunction("mag(vectors)") 
magnitudeCalcFilter.Update()

#------------ CHALLENGE THREE ----------------------
points = vtk.vtkPoints()
grid = magnitudeCalcFilter.GetOutput()
grid.GetPoints(points)
scalars = grid.GetPointData().GetArray("magnitude")

ugrid = vtk.vtkUnstructuredGrid()
ugrid.SetPoints(points)
ugrid.GetPointData().SetScalars(scalars)

for i in range (0, grid.GetNumberOfCells()):
    cell = grid.GetCell(i)
    ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())

subset = vtk.vtkMaskPoints()
subset.SetOnRatio(50)
subset.RandomModeOn()
subset.SetInputData(ugrid)

pointsGlyph = vtk.vtkVertexGlyphFilter()
pointsGlyph.SetInputConnection(subset.GetOutputPort())
#pointsGlyph.SetInputData(ugrid)
pointsGlyph.Update()

pointsMapper = vtk.vtkPolyDataMapper()
pointsMapper.SetInputConnection(pointsGlyph.GetOutputPort())
pointsMapper.SetScalarModeToUsePointData()

pointsActor = vtk.vtkActor()
pointsActor.SetMapper(pointsMapper)

#------------ CHALLENGE FOUR ----------------------
scalarRange = ugrid.GetPointData().GetScalars().GetRange()
print(scalarRange)

isoFilter = vtk.vtkContourFilter()
isoFilter.SetInputData(ugrid)
isoFilter.GenerateValues(10, scalarRange)

isoMapper = vtk.vtkPolyDataMapper()
isoMapper.SetInputConnection(isoFilter.GetOutputPort())

isoActor = vtk.vtkActor()
isoActor.SetMapper(isoMapper)
isoActor.GetProperty().SetOpacity(0.5)

#------------ CHALLENGE FIVE ----------------------
subset = vtk.vtkMaskPoints()
subset.SetOnRatio(10)
subset.RandomModeOn()
subset.SetInputConnection(rectGridReader.GetOutputPort())

lut = vtk.vtkLookupTable()
lut.SetNumberOfColors(256)
lut.SetHueRange(0.667, 0.0)
lut.SetVectorModeToMagnitude()
lut.Build()

hh = vtk.vtkHedgeHog()
hh.SetInputConnection(subset.GetOutputPort())
hh.SetScaleFactor(0.001)

hhm = vtk.vtkPolyDataMapper()
hhm.SetInputConnection(hh.GetOutputPort())
hhm.SetLookupTable(lut)
hhm.SetScalarVisibility(True)
hhm.SetScalarModeToUsePointFieldData()
hhm.SelectColorArray('vectors')
hhm.SetScalarRange((rectGridReader.GetOutput().GetPointData().GetVectors().GetRange(-1)))

hha = vtk.vtkActor()
hha.SetMapper(hhm)

#------------ RENDERER, RENDER WINDOW, AND INTERACTOR ----------------------
#Option 1: Default vtk render window
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.5, 0.5, 0.5)
#renderer.AddActor(outlineActor)
#renderer.AddActor(gridGeomActor)
#renderer.AddActor(pointsActor)
#renderer.AddActor(isoActor)
renderer.AddActor(hha)
renderer.ResetCamera()

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)
renderWindow.Render()

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renderWindow)
iren.Start()