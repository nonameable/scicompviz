import vtk

reader = vtk.vtkRectilinearGridReader()
reader.SetFileName("../data/jet4_0.500.vtk")
reader.Update()
output = reader.GetOutput()

xmi, xma, ymi, yma, zmi, zma = output.GetBounds()

# Color Transfer Function and LookUpTable
# Create transfer mapping scalar value to color
colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(0.15, 0.0, 0.0, 1.0)
colorTransferFunction.AddRGBPoint(0.3, 0.0, 1.0, 0.0)

tableSize = 30

lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(tableSize)
lut.Build()

for i in range(0,tableSize):
    rgb = list(colorTransferFunction.GetColor(float(i)/tableSize))+[0.5]
    lut.SetTableValue(i,rgb)
        

# A plane for the seeds
plane = vtk.vtkPlaneSource()
plane.SetOrigin(0, 0, 0)
plane.SetPoint1(xma, 0, 0)
plane.SetPoint2(0, 0, zma)
plane.SetXResolution(20)
plane.SetYResolution(20)

# Add the outline of the plane
outline = vtk.vtkOutlineFilter()
outline.SetInputData(plane.GetOutput())
outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())
outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetColor(1,1,1)

# Compute streamlines
streamline = vtk.vtkStreamTracer()
streamline.SetSourceConnection(plane.GetOutputPort())
streamline.SetInputConnection(reader.GetOutputPort())
streamline.SetIntegrationDirectionToForward()
#streamline.SetIntegrationDirectionToBackward()
#streamline.SetIntegrationDirectionToBoth()
streamline.SetMaximumPropagation(1)
streamline.SetComputeVorticity(True)

# Visualize stream as ribbons (= Stream ribbons); i.e. we need to pass the streamlines through the ribbon filter
streamRibbons = vtk.vtkRibbonFilter()
streamRibbons.SetInputConnection(streamline.GetOutputPort())
streamRibbons.SetWidth(0.01)
streamRibbons.Update()

streamRibbonsMapper = vtk.vtkPolyDataMapper()
streamRibbonsMapper.SetScalarModeToUsePointFieldData()
streamRibbonsMapper.SetInputConnection(streamRibbons.GetOutputPort())

streamRibbonsActor = vtk.vtkActor()
streamRibbonsActor.GetProperty().SetOpacity(0.5)
streamRibbonsActor.GetProperty().SetColor(0.3, 0.5, 0.9)
streamRibbonsActor.SetMapper(streamRibbonsMapper)

# Pass the streamlines to the mapper
streamlineMapper = vtk.vtkPolyDataMapper()
streamlineMapper.SetLookupTable(lut)
streamlineMapper.SetInputConnection(streamline.GetOutputPort())
streamlineMapper.SetScalarVisibility(True)
streamlineMapper.SetScalarModeToUsePointFieldData()
streamlineMapper.SelectColorArray('vectors')
streamlineMapper.SetScalarRange((reader.GetOutput().GetPointData().GetVectors().GetRange(-1)))

# Pass the mapper to the actor
streamlineActor = vtk.vtkActor()
streamlineActor.SetMapper(streamlineMapper)
streamlineActor.GetProperty().SetLineWidth(2.0)

# Add the outline of the data set
gOutline = vtk.vtkRectilinearGridOutlineFilter()
gOutline.SetInputData(output)
gOutlineMapper = vtk.vtkPolyDataMapper()
gOutlineMapper.SetInputConnection(gOutline.GetOutputPort())
gOutlineActor = vtk.vtkActor()
gOutlineActor.SetMapper(gOutlineMapper)
gOutlineActor.GetProperty().SetColor(0.5,0.5,0.5)

# Rendering / Window
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.0, 0.0, 0.0)
#renderer.AddActor(streamlineActor)
renderer.AddActor(streamRibbonsActor)
renderer.AddActor(outlineActor)
renderer.AddActor(gOutlineActor)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)
renderWindow.Render()

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(renderWindow)
interactor.Initialize()
interactor.Start()
