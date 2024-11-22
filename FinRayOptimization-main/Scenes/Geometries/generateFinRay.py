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



############################### PAREDES ############################## 

############################### GRILLA ############################## 
# Cálculo de la longitud disponible en el eje Z
longitud_disponible_z = Constants.Depth - 2 * Constants.sangria_grilla

# Evitar divisiones por cero
if Constants.cantidad_grilla_vertical > 1:
    separacion_grilla_vertical = longitud_disponible_z / (Constants.cantidad_grilla_vertical - 1)
else:
    separacion_grilla_vertical = longitud_disponible_z  # Si solo hay una línea, ocupa todo el espacio disponible

cilindros_grilla = []

for i in range(Constants.cantidad_grilla_vertical):
    z_pos = Constants.sangria_grilla + i * separacion_grilla_vertical
    if z_pos > Constants.Depth - Constants.sangria_grilla:
        break  # Evitar superar el límite superior

    # Coordenadas fijas en X y Y (valores negativos en X)
    x_inferior = -Constants.GripperWidth
    y_inferior = 0
    x_superior = -Constants.WallThickness
    y_superior = Constants.GripperHeight + Constants.GripperHeightGift

    # Coordenadas del punto inicial y final
    x0 = x_inferior
    y0 = y_inferior
    z0 = z_pos

    x1 = x_superior
    y1 = y_superior
    z1 = z_pos

    # Vector dirección del cilindro
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0

    # Crear el cilindro
    cilindro = factory.addCylinder(
        x0, y0, z0,      # Origen del cilindro
        dx, dy, dz,      # Vector dirección
        Constants.radio_cilindro_grilla  # Radio del cilindro
    )

    # Almacenar el cilindro
    cilindros_grilla.append((3, cilindro))

# Sincronizar la geometría
factory.synchronize()
############################### GRILLA ############################## 


############################### BARRAS INTERNAS ############################## 
BarPositions = np.linspace(0, InnerGripperHeight, Constants.NBars+2)
for BarPosition in BarPositions[1:-1]:
    print(f"BarPosition:{BarPosition}")
    StepWidth = 0.1  
    BarTotalLength = np.tan(Phi)*BarPosition
    
    BarTopLength = np.tan(Phi)*(BarPosition-Constants.BarHeightThin/2)
    BarBottomLength = np.tan(Phi)*(BarPosition+Constants.BarHeightThin/2)  
    if BarTotalLength < Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P1Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P2Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        P3Bar = factory.addPoint(BarBottomLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)
        
        PointTags += [P0Bar, P1Bar, P2Bar,P3Bar]
    
    if BarTotalLength > Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P1Bar = factory.addPoint(BarTopLength-Constants.BarThinLength,InnerGripperHeight-(BarPosition-Constants.BarHeightThin/2),0)
        P2Bar = factory.addPoint(BarTopLength-Constants.BarThinLength-StepWidth,InnerGripperHeight-(BarPosition-Constants.BarHeightThick/2),0)        
        P3Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition-Constants.BarHeightThick/2),0)
        P4Bar = factory.addPoint(0,InnerGripperHeight-(BarPosition+Constants.BarHeightThick/2),0)        
        P5Bar = factory.addPoint(BarBottomLength-Constants.BarThinLength-StepWidth,InnerGripperHeight-(BarPosition+Constants.BarHeightThick/2),0)        
        P6Bar = factory.addPoint(BarBottomLength-Constants.BarThinLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)  
        P7Bar = factory.addPoint(BarBottomLength,InnerGripperHeight-(BarPosition+Constants.BarHeightThin/2),0)      
        PointTags += [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar,P5Bar,P6Bar,P7Bar]
############################### BARRAS INTERNAS ############################## 

############################### LINEAS 2D Y SUP?############################## 
LineTags = addLines(PointTags)
WireTag = factory.addWire(LineTags)
SurfaceDimTag = (2,factory.addPlaneSurface([WireTag]))
############################### LINEAS 2D Y SUP? ############################## 

############################### LE DA SUPERFICIE ############################## 
ExtrudeOut = factory.extrude([SurfaceDimTag], 0, 0, Constants.Depth)
HalfDimTag = ExtrudeOut[1]
############################### LE DA SUPERFICIE ############################## 

############################### DUPLICA LA FIGURA ############################## 
CopyDimTags = factory.copy([HalfDimTag])
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)
############################### DUPLICA LA FIGURA ############################## 

factory.fuse(CopyDimTags, [HalfDimTag])




# Sincronizar la geometría
factory.synchronize()
# Visualizar la geometría hasta este punto
launchGUI()
exit()




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