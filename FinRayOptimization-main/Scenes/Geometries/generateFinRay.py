############################### INICIO ##############################
import gmsh
import numpy as np
import Constants
gmsh.initialize()
launchGUI = gmsh.fltk.run 
factory = gmsh.model.occ
############################### INICIO ##############################

############################### CREAR LINEAS ##############################
def addLines(PointTags, Close=True):
    N = len(PointTags)
    EndIdx = N
    LineTags = [] 
    if Close is False:
        EndIdx = EndIdx-1
    for i in range(EndIdx):
        print(i)
        LineTags.append(factory.addLine(PointTags[i], PointTags[(i+1)%N]))
    return LineTags
############################### CREAR LINEAS ##############################      

############################### PAREDES ##############################     
InnerGripperHeight = (Constants.GripperWidth-Constants.WallThickness)/np.cos(Constants.Theta)
Phi = np.arctan2(Constants.GripperWidth-Constants.WallThickness,InnerGripperHeight)


                        #(30-3= 27,0,0)
P0 = factory.addPoint(Constants.GripperWidth-Constants.WallThickness, 0, 0)
P1 = factory.addPoint(Constants.GripperWidth, 0, 0)
P2= factory.addPoint(Constants.WallThickness, Constants.GripperHeight+Constants.GripperHeightGift,0)
P3= factory.addPoint(0, Constants.GripperHeight+Constants.GripperHeightGift,0)
P4 = factory.addPoint(0, InnerGripperHeight, 0)
PointTags = [P0,P1,P2,P3,P4]

LineTags = addLines(PointTags)
WireTag = factory.addWire(LineTags)
SurfaceDimTag = (2,factory.addPlaneSurface([WireTag]))

############################### PAREDES ############################## 

############################### GRILLA ############################## 
# Cálculo de la longitud disponible en el eje Z
longitud_disponible_z = Constants.Depth - 2 * Constants.sangria_grilla

# Evitar divisiones por cero
if Constants.cantidad_grilla_vertical > 1:
    separacion_grilla_vertical = longitud_disponible_z / (Constants.cantidad_grilla_vertical - 1)
else:
    separacion_grilla_vertical = longitud_disponible_z  # Si solo hay una línea, ocupa todo el espacio disponible

lineas_grilla_vertical = []

for i in range(Constants.cantidad_grilla_vertical):
    z_pos = Constants.sangria_grilla + i * separacion_grilla_vertical
    if z_pos > Constants.Depth - Constants.sangria_grilla:
        break  # Evitar superar el límite superior

    # Coordenadas fijas en X y Y
    x_inferior = -Constants.GripperWidth
    y_inferior = 0
    x_superior = -Constants.WallThickness
    y_superior = Constants.GripperHeight + Constants.GripperHeightGift

    # Crear los puntos para la línea vertical
    punto_inferior = factory.addPoint(x_inferior, y_inferior, z_pos)
    punto_superior = factory.addPoint(x_superior, y_superior, z_pos)

    # Crear la línea vertical
    linea_vertical = factory.addLine(punto_inferior, punto_superior)
    lineas_grilla_vertical.append(linea_vertical)

# Sincronizar la geometría
factory.synchronize()
############################### GRILLA ############################## 



# BarPositions = np.linspace(0, InnerGripperHeight, Constants.NBars+2)
# for BarPosition in BarPositions[1:-1]:
#     print(f"BarPosition:{BarPosition}")
#     StepWidth = 0.1
    
#     BarTotalLength = np.tan(Phi)*BarPosition
    
#     BarTopLength = np.tan(Phi)*(BarPosition-Constants.BarHeightThin/2)
#     BarBottomLength = np.tan(Phi)*(BarPosition+Constants.BarHeightThin/2)
    
#     if BarTotalLength < Constants.BarThinLength:
#         P0Bar = factory.addPoint(BarTopLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
#         P1Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
#         P2Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
#         P3Bar = factory.addPoint(BarBottomLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        
#         PointTags += [P0Bar, P1Bar, P2Bar,P3Bar]
    
#     if BarTotalLength > Constants.BarThinLength:
#         P0Bar = factory.addPoint(BarTopLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
#         P1Bar = factory.addPoint(BarTopLength-Constants.BarThinLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
#         P2Bar = factory.addPoint(BarTopLength-Constants.BarThinLength-StepWidth,InnerGripperHeight-(BarPosition-Constants.BarHeightThick/2),0)        
#         P3Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition-Constants.BarHeightThick/2),0)
#         P4Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition+Constants.BarHeightThick/2),0)        
#         P5Bar = factory.addPoint(BarBottomLength-Constants.BarThinLength-StepWidth,InnerGripperHeight-(BarPosition+Constants.BarHeightThick/2),0)        
#         P6Bar = factory.addPoint(BarBottomLength-Constants.BarThinLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)  
#         P7Bar = factory.addPoint(BarBottomLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        
#         PointTags += [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar,P5Bar,P6Bar,P7Bar]



ExtrudeOut = factory.extrude([SurfaceDimTag], 0, 0, Constants.Depth)
HalfDimTag = ExtrudeOut[1]
CopyDimTags = factory.copy([HalfDimTag])
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)
factory.fuse(CopyDimTags, [HalfDimTag])
print(f"ExtrudeOut:{ExtrudeOut}")

factory.synchronize()

# defineMeshSizes(2)
gmsh.model.mesh.generate(3)
gmsh.write("FinRay.vtk")
gmsh.model.mesh.clear()
gmsh.model.mesh.generate(2)
gmsh.model.mesh.refine()
gmsh.model.mesh.refine()
gmsh.write("FinRay.stl")

factory.synchronize()

launchGUI()