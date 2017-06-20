#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 16:37:43 2017

@author: damaderu
"""

import vtk
#help(vtk.vtkRectilinearGridReader())

rectGridReader = vtk.vtkRectilinearGridReader()
rectGridReader.SetFileName("data/jet4_0.500.vtk")
# do not forget to call "Update()" at the end of the reader
rectGridReader.Update()


rectGridOutline = vtk.vtkRectilinearGridOutlineFilter()
rectGridOutline.SetInputData(rectGridReader.GetOutput())

rectGridFilter = vtk.vtkRectilinearGridGeometryFilter() 
rectGridFilter.SetInputData(rectGridReader.GetOutput())

rectGridOutlineMapper = vtk.vtkPolyDataMapper()
rectGridOutlineMapper.SetInputConnection(rectGridOutline.GetOutputPort())

rectGridGeomMapper = vtk.vtkPolyDataMapper()
rectGridGeomMapper.SetInputConnection(rectGridFilter.GetOutputPort()) # added line

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(rectGridOutlineMapper)
outlineActor.GetProperty().SetColor(0, 0, 3) # changed the color to blue

gridGeomActor = vtk.vtkActor()
gridGeomActor.SetMapper(rectGridGeomMapper)
gridGeomActor.GetProperty().SetRepresentationToWireframe()


gridGeomActor.GetProperty().SetColor(0, 0, 0) # changed the color to a red 
gridGeomActor.GetProperty().SetOpacity(0.5);

magnitudeCalcFilter = vtk.vtkArrayCalculator()
magnitudeCalcFilter.SetInputConnection(rectGridReader.GetOutputPort())
magnitudeCalcFilter.AddVectorArrayName('vectors')
# Set up here the array that is going to be used for the computation ('vectors')
magnitudeCalcFilter.SetResultArrayName('magnitude')
magnitudeCalcFilter.SetFunction("mag(vectors)")
# Set up here the function that calculates the magnitude of a vector
magnitudeCalcFilter.Update()


#Extract the data from the result of the vtkCalculator
points = vtk.vtkPoints()
grid = magnitudeCalcFilter.GetOutput()
grid.GetPoints(points)
scalars = grid.GetPointData().GetArray('magnitude')

#Create an unstructured grid that will contain the points and scalars data
ugrid = vtk.vtkUnstructuredGrid()
ugrid.SetPoints(points)
ugrid.GetPointData().SetScalars(scalars)

#Populate the cells in the unstructured grid using the output of the vtkCalculator
for i in range (0, grid.GetNumberOfCells()):
    cell = grid.GetCell(i)
    ugrid.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
    
    
#There are too many points, let's filter the points
subset = vtk.vtkMaskPoints()
subset.SetOnRatio(5)
subset.RandomModeOn()
subset.SetRandomModeType(1)
subset.SetInputData(ugrid)

#Make a vtkPolyData with a vertex on each point.
pointsGlyph = vtk.vtkVertexGlyphFilter()
pointsGlyph.SetInputConnection(subset.GetOutputPort())
#pointsGlyph.SetInputData(ugrid)
pointsGlyph.Update()

pointsMapper = vtk.vtkPolyDataMapper()
pointsMapper.SetInputConnection(pointsGlyph.GetOutputPort())
pointsMapper.SetScalarModeToUsePointData()

pointsActor = vtk.vtkActor()
pointsActor.SetMapper(pointsMapper)


scalarRange = ugrid.GetPointData().GetScalars().GetRange()
print(scalarRange)

isoFilter = vtk.vtkContourFilter()
isoFilter.SetInputData(ugrid)
isoFilter.GenerateValues(10, scalarRange) 

# you may change scalarRange for newScalarRange to see the result
#newScalarRange = (5.7123318, 9.7623123)
#isoFilter.GenerateValues(10, newScalarRange) 


isoMapper = vtk.vtkPolyDataMapper()
isoMapper.SetInputConnection(isoFilter.GetOutputPort())

isoActor = vtk.vtkActor()
isoActor.SetMapper(isoMapper)
isoActor.GetProperty().SetOpacity(0.5)

subset = vtk.vtkMaskPoints()
subset.SetOnRatio(10)
subset.RandomModeOn()
subset.SetInputConnection(rectGridReader.GetOutputPort())

#vtk.vtkColorTransferFunction()
#vtk.vtkLookupTable()
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


renderer = vtk.vtkRenderer()
renderer.AddActor(pointsActor)    
renderer.AddActor(outlineActor)
renderer.AddActor(isoActor)
renderer.AddActor(gridGeomActor)
renderer.AddActor(hha)

renderer.SetBackground(0, 0, 0)
renderer.ResetCamera()
renderer.GetActiveCamera().Elevation(60.0)
renderer.GetActiveCamera().Azimuth(30.0)
renderer.GetActiveCamera().Zoom(1.0)




renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)
renderWindow.Render()


iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renderWindow)
iren.Start()