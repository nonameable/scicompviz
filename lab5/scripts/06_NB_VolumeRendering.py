import vtk

#------------READER ----------------------
rectGridReader = vtk.vtkRectilinearGridReader()
rectGridReader.SetFileName("D:/Notebooks_Bogota2017/SS_2017/data/jet4_0.500.vtk")
rectGridReader.Update()
#------------END READER ------------------

#------------ FILTER: CALCULATE VECTOR MAGNITUDE ----------------------
magnitudeCalcFilter = vtk.vtkArrayCalculator()
magnitudeCalcFilter.SetInputConnection(rectGridReader.GetOutputPort())
magnitudeCalcFilter.AddVectorArrayName('vectors')
magnitudeCalcFilter.SetResultArrayName('magnitude')
magnitudeCalcFilter.SetFunction("mag(vectors)") 
magnitudeCalcFilter.Update()
#------------END CALCULATE VECTOR MAGNITUDE ----------------------

#------------FILTER: RECTILINEAR GRID TO IMAGE DATA-----------
bounds = magnitudeCalcFilter.GetOutput().GetBounds()
dimensions = magnitudeCalcFilter.GetOutput().GetDimensions()
origin = (bounds[0], bounds[2], bounds[4])
spacing = ( (bounds[1]-bounds[0])/dimensions[0], 
            (bounds[3]-bounds[2])/dimensions[1],
            (bounds[5]-bounds[4])/dimensions[2])

imageData = vtk.vtkImageData()
imageData.SetOrigin(origin)
imageData.SetDimensions(dimensions)
imageData.SetSpacing(spacing)

probeFilter = vtk.vtkProbeFilter()
probeFilter.SetInputData(imageData)
probeFilter.SetSourceData(magnitudeCalcFilter.GetOutput())
probeFilter.Update()

imageData2 = probeFilter.GetImageDataOutput()
#------------END RECTILINEAR GRID TO IMAGE DATA-----------

##------------FILTER, MAPPER, AND ACTOR: VOLUME RENDERING -------------------
# Create transfer mapping scalar value to opacity
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(0, 0.2)
opacityTransferFunction.AddPoint(14, 0.0)

# Create transfer mapping scalar value to color
colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(0.5, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(2.0, 0.0, 0.0, 1.0)
colorTransferFunction.AddRGBPoint(6.0, 0.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(14.0, 0.0, 0.2, 0.0)

# The property describes how the data will look
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.ShadeOff()
volumeProperty.SetInterpolationTypeToLinear()


# The mapper / ray cast function know how to render the data
#volumeMapper = vtk.vtkProjectedTetrahedraMapper()
#volumeMapper = vtk.vtkUnstructuredGridVolumeZSweepMapper()
volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
#volumeMapper = vtk.vtkUnstructuredGridVolumeRayCastMapper()
volumeMapper.SetInputData(imageData2)

# The volume holds the mapper and the property and
# can be used to position/orient the volume
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

##------------END VOLUME RENDERING ----------------------

#---------RENDERER, RENDER WINDOW, AND INTERACTOR ----------
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.5, 0.5, 0.5)
renderer.AddVolume(volume)
renderer.ResetCamera()

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)
renderWindow.Render()

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renderWindow)
iren.Start()
#---------END RENDERER, RENDER WINDOW, AND INTERACTOR -------