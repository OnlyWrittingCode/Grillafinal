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

# Calcular la longitud total en Y
longitud_total_y = y2 - y1

# Calcular las posiciones Y inicial y final con sangría
y_inicio_con_sangria = y1 + Constants.sangria_grilla_horizontal
y_fin_con_sangria = y2 - Constants.sangria_grilla_horizontal

# Calcular los valores de t correspondientes a las posiciones Y con sangría
t_inicio = (y_inicio_con_sangria - y1) / (y2 - y1)
t_fin = (y_fin_con_sangria - y1) / (y2 - y1)

# Asegurar que t_inicio y t_fin están entre 0 y 1
t_inicio = max(0, min(1, t_inicio))
t_fin = max(0, min(1, t_fin))

# Generar los valores de t ajustados
t_values = np.linspace(t_inicio, t_fin, cantidad_cilindros_horizontal)

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
    dz_cilindro = Constants.Depth + Constants.borde

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


# Copiar y simetrizar el exterior
CopyDimTags_finaltotal= factory.copy([HalfDimTag])
factory.synchronize()  # Sincronizar antes de simetrizar
factory.symmetrize(CopyDimTags_finaltotal, 0, 0, -1, Constants.Depth+Constants.borde)

# Fusionar las dos mitades de la garra para obtener la garra completa
fuse_full_gripper = factory.fuse([HalfDimTag], CopyDimTags_finaltotal)
full_gripper = fuse_full_gripper[0]  # Entidades agregadas (resultado de la fusión)

# Sincronizar después de la fusión
factory.synchronize()

############################### BASE DE GARRA ##############################

# Definir los parámetros de las alas
wing_extension = 10  # Extensión lateral de las alas en milímetros (ajusta según necesites)
wing_height = 1      # Altura de las alas en milímetros (desde la parte inferior de la base)

# Crear los puntos de la base original
base0 = factory.addPoint(Constants.GripperWidth + Constants.base_extra, 0, 0)
base1 = factory.addPoint(Constants.GripperWidth + Constants.base_extra, -10 - Constants.abajo_base_extra, 0)
base2 = factory.addPoint(-Constants.GripperWidth - Constants.base_extra, -10 - Constants.abajo_base_extra, 0)
base3 = factory.addPoint(-Constants.GripperWidth - Constants.base_extra, 0, 0)

point_tag_base = [base0, base1, base2, base3]

# Crear las líneas y la superficie de la base
Line_tags_base = addLines(point_tag_base)
WireTag_base = factory.addWire(Line_tags_base)
SurfaceDimTag_base = (2, factory.addPlaneSurface([WireTag_base]))

# Extruir la base
ExtrudeOut_base = factory.extrude([SurfaceDimTag_base], 0, 0, (Constants.Depth + Constants.borde) * 2)
dimtag_base = ExtrudeOut_base[1]

# Sincronizar después de extruir la base
factory.synchronize()

# Crear las alas como cajas y fusionarlas con la base

# Coordenadas comunes
y0_wing = -10 - Constants.abajo_base_extra
z0_wing = 0
dx_wing = wing_extension
dy_wing = wing_height
dz_wing = (Constants.Depth + Constants.borde) * 2

# Ala derecha
x0_right_wing = Constants.GripperWidth + Constants.base_extra
right_wing = factory.addBox(x0_right_wing, y0_wing, z0_wing, dx_wing, dy_wing, dz_wing)

# Ala izquierda
x0_left_wing = -Constants.GripperWidth - Constants.base_extra - wing_extension
left_wing = factory.addBox(x0_left_wing, y0_wing, z0_wing, dx_wing, dy_wing, dz_wing)

# Sincronizar después de crear las alas
factory.synchronize()

# Fusionar la base con el ala derecha
fuse_result_base_right_wing = factory.fuse([dimtag_base], [(3, right_wing)])
base_with_right_wing = fuse_result_base_right_wing[0]
factory.synchronize()

# Fusionar el resultado anterior con el ala izquierda
fuse_result_base_wings = factory.fuse(base_with_right_wing, [(3, left_wing)])
base_with_wings = fuse_result_base_wings[0]
factory.synchronize()

############################### CORTE DE LA BASE ##############################

# Realizar el corte: base con alas - garra completa
cut_result_base = factory.cut(base_with_wings, full_gripper)

# Obtener el volumen resultante después del corte
if cut_result_base[0]:
    base_con_hueco = cut_result_base[0]
    print("Base con alas después del corte:", base_con_hueco)
else:
    print("Error: No se creó ninguna entidad durante el corte de la base.")

# Sincronizar después del corte
factory.synchronize()

############################### CORTE DE LA BASE ##############################




############################### CILINDRO EN EL CENTRO ##############################

from math import sqrt

# Punto de inicio original del cilindro (en la pared izquierda)
x0_original = -Constants.GripperWidth + Constants.WallThickness  # Justo dentro de la pared izquierda
y0_original = Constants.GripperHeight / 2  # Altura central en Y
z0_original = Constants.Depth + Constants.borde  # Centro en Z después de la simetría

# Punto final original del cilindro (en la pared derecha)
x1_original = Constants.GripperWidth - Constants.WallThickness  # Justo dentro de la pared derecha
y1_original = y0_original - 50  # Inclinación hacia abajo (ajusta según necesites)
z1_original = z0_original  # Misma posición en Z

# Calcular el punto central del cilindro
x_centro = (x0_original + x1_original) / 2
y_centro = (y0_original + y1_original) / 2
z_centro = (z0_original + z1_original) / 2

# Calcular el vector dirección original
dx_original = x1_original - x0_original
dy_original = y1_original - y0_original
dz_original = z1_original - z0_original

# Calcular la longitud original del cilindro
longitud_original = sqrt(dx_original**2 + dy_original**2 + dz_original**2)

# Vector dirección unitario
ux = dx_original / longitud_original
uy = dy_original / longitud_original
uz = dz_original / longitud_original

# Definir el incremento de longitud en cada extremo
incremento = 20  # En milímetros (ajusta este valor según necesites)

# Calcular la nueva longitud total del cilindro
longitud_nueva = longitud_original + 2 * incremento

# Calcular los nuevos puntos inicial y final
x0_nuevo = x_centro - (longitud_nueva / 2) * ux
y0_nuevo = y_centro - (longitud_nueva / 2) * uy
z0_nuevo = z_centro - (longitud_nueva / 2) * uz

x1_nuevo = x_centro + (longitud_nueva / 2) * ux
y1_nuevo = y_centro + (longitud_nueva / 2) * uy
z1_nuevo = z_centro + (longitud_nueva / 2) * uz

# Calcular el nuevo vector dirección
dx_nuevo = x1_nuevo - x0_nuevo
dy_nuevo = y1_nuevo - y0_nuevo
dz_nuevo = z1_nuevo - z0_nuevo

# Definir el radio del cilindro
radio_cilindro_central = 1  # Ajusta según el diámetro del cable

# Crear el cilindro con los nuevos parámetros
cilindro_central_tag = factory.addCylinder(
    x0_nuevo, y0_nuevo, z0_nuevo,  # Nuevo punto de inicio
    dx_nuevo, dy_nuevo, dz_nuevo,  # Nuevo vector dirección
    radio_cilindro_central  # Radio del cilindro
)

# Sincronizar la geometría
factory.synchronize()

# Visualizar la figura con el cilindro antes del corte
launchGUI()

# Realizar el corte de la garra completa con el cilindro central
cut_result_cilindro = factory.cut(full_gripper, [(3, cilindro_central_tag)])

# Obtener el volumen resultante después del corte
if cut_result_cilindro[0]:
    full_gripper_con_hueco = cut_result_cilindro[0]
    print("Garra con hueco para el cable:", full_gripper_con_hueco)
else:
    print("Error: No se creó ninguna entidad durante el corte con el cilindro central.")

# Sincronizar después del corte
factory.synchronize()

############################### CILINDRO EN EL CENTRO ##############################





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