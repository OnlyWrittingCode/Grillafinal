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

PointTags_exterior = PointTags.copy()
############################### PAREDES ############################## 

############################### Soporte ############################## 
soporte1 = factory.addPoint(Constants.GripperWidth, -10, 0)
soporte2 = factory.addPoint(Constants.GripperWidth-6, -10, 0)
soporte3 = factory.addPoint(Constants.GripperWidth-6, -7, 0)
soporte4 = factory.addPoint(Constants.GripperWidth-3, -7, 0)
soporte5 = factory.addPoint(Constants.GripperWidth-3, -3, 0)
soporte6 = factory.addPoint(0, -3, 0)
soporte7 = factory.addPoint(0, 0, 0)

point_tag_soporte = [P1,soporte1,soporte2,soporte3,soporte4,soporte5,soporte6,soporte7,P0]

############################### Soporte ##############################

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

############################### GRILLA HORIZONTAL ##############################
# Puntos de la pared inclinada en el lado izquierdo (coordenadas negativas)
x1 = -Constants.GripperWidth
y1 = 0
z1 = 0

x2 = -Constants.WallThickness
y2 = Constants.GripperHeight + Constants.GripperHeightGift
z2 = 0

# Vector dirección de la línea
dx_line = x2 - x1
dy_line = y2 - y1

# Número de cilindros horizontales
cantidad_cilindros_horizontal = Constants.cantidad_grilla_horizontal

# Valores de t para distribuir los cilindros a lo largo de la línea
t_values = np.linspace(0, 1, cantidad_cilindros_horizontal)

# Definir el desplazamiento en X
offset_x = -1  # Ajusta este valor según sea necesario

for t in t_values:
    # Posición del cilindro a lo largo de la línea
    x = x1 + t * dx_line + offset_x
    y = y1 + t * dy_line
    z = 0

    # Vector perpendicular a la línea en 2D
    dx_perp = -dy_line
    dy_perp = dx_line

    # Normalizar el vector perpendicular
    length_perp = np.sqrt(dx_perp**2 + dy_perp**2)
    dx_perp_norm = dx_perp / length_perp
    dy_perp_norm = dy_perp / length_perp

    # Cálculo del desplazamiento
    shift_amount = (Constants.WallThickness / 2) - (Constants.radio_cilindro_grilla / 2)

    # Ajustar la posición del cilindro
    x -= dx_perp_norm * shift_amount
    y -= dy_perp_norm * shift_amount

    # Definir las dimensiones del cilindro
    x0 = x
    y0 = y
    z0 = 0  # Iniciamos desde el margen en Z

    dx_cilindro = 0
    dy_cilindro = 0
    dz_cilindro = Constants.Depth - 2 * 0

    # Crear el cilindro
    cilindro = factory.addCylinder(
        x0, y0, z0,
        dx_cilindro, dy_cilindro, dz_cilindro,
        Constants.radio_cilindro_grilla
    )

    # Agregar el cilindro a la lista
    cilindros_grilla.append((3, cilindro))

# Sincronizar la geometría
factory.synchronize()
############################### GRILLA HORIZONTAL ##############################

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
LineTags_soporte = addLines(point_tag_soporte)
Line_tags_exterior = addLines(PointTags_exterior)

WireTag = factory.addWire(LineTags)
WireTag_soporte = factory.addWire(LineTags_soporte)
WireTag_exterior = factory.addWire(Line_tags_exterior)

SurfaceDimTag = (2,factory.addPlaneSurface([WireTag]))
SurfaceDimTag_soporte = (2,factory.addPlaneSurface([WireTag_soporte]))
SurfaceDimTag_exterior = (2,factory.addPlaneSurface([WireTag_exterior]))
############################### LINEAS 2D Y SUP? ############################## 

############################### LE DA SUPERFICIE ############################## 
ExtrudeOut = factory.extrude([SurfaceDimTag], 0, 0, Constants.Depth)
ExtrudeOut_soporte = factory.extrude([SurfaceDimTag_soporte], 0, 0, Constants.Depth+Constants.borde)
ExtrudeOut_exterior = factory.extrude([SurfaceDimTag_exterior], 0, 0, Constants.Depth+Constants.borde)

HalfDimTag = ExtrudeOut[1]
HalfDimTag_soporte = ExtrudeOut_soporte[1]
HalfDimTag_exterior = ExtrudeOut_exterior[1]
############################### LE DA SUPERFICIE ############################## 

############################### DUPLICA LA FIGURA ##############################
# Copiar y simetrizar la garra
CopyDimTags = factory.copy([HalfDimTag])
factory.synchronize()  # Sincronizar antes de simetrizar
factory.symmetrize(CopyDimTags, 1, 0, 0, 0)

# Copiar y simetrizar el soporte
CopyDimTags_soporte = factory.copy([HalfDimTag_soporte])
factory.synchronize()  # Sincronizar antes de simetrizar
factory.symmetrize(CopyDimTags_soporte, 1, 0, 0, 0)

# Copiar y simetrizar el exterior
CopyDimTags_exterior= factory.copy([HalfDimTag_exterior])
factory.synchronize()  # Sincronizar antes de simetrizar
factory.symmetrize(CopyDimTags_exterior, 1, 0, 0, 0)


# Realizar la fusión de la garra
fuse_result_garra = factory.fuse(CopyDimTags, [HalfDimTag])
garra_final = fuse_result_garra[0]  # Entidades agregadas de la garra

# Realizar la fusión del soporte
fuse_result_soporte = factory.fuse(CopyDimTags_soporte, [HalfDimTag_soporte])
soporte_final = fuse_result_soporte[0]  # Entidades agregadas del soporte

fuse_result_exterior = factory.fuse(CopyDimTags_exterior, [HalfDimTag_exterior])
exterior_final =  fuse_result_exterior[0]

# Fusionar garra y soporte en una sola entidad final
fuse_result_total = factory.fuse(garra_final, soporte_final)
garra_soporte_final = fuse_result_total[0]  # Entidades agregadas de la fusión total

fuse_total = factory.fuse(garra_soporte_final,exterior_final)
total_final = fuse_total[0]



# Imprimir para verificar
print("Garra Final después de la fusión:", total_final)

# Sincronizar después de la fusión total
factory.synchronize()
############################### DUPLICA LA FIGURA ##############################

############################### OPERACIÓN DE CORTE ##############################
# Definir las entidades a cortar y las herramientas de corte
objects_to_cut = total_final  # Lista de entidades a cortar
cutting_tools = cilindros_grilla  # Lista de cilindros que harán el corte (lista de tuplas (dim, tag))

# Verificar los datos antes de realizar la operación de corte
print("Entidades a cortar (objects_to_cut):", objects_to_cut)
print("Herramientas de corte (cutting_tools):", cutting_tools)

# Realizar la operación de corte
cut_result = factory.cut(objects_to_cut, cutting_tools)
added_cut = cut_result[0]  # Entidades agregadas (resultado del corte)
removed_cut = cut_result[1]  # Entidades removidas durante el corte

# Verificar y asignar
if added_cut:
    HalfDimTag = added_cut[0]  # Asignar el volumen resultante del corte
    print("Garra cortada:", HalfDimTag)
else:
    print("Error: No se crearon entidades durante el corte.")
############################### OPERACIÓN DE CORTE ##############################


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
exit()