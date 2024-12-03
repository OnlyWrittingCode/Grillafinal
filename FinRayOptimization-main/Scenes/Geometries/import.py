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
        EndIdx = EndIdx - 1
    for i in range(EndIdx):
        print(i)
        LineTags.append(factory.addLine(PointTags[i], PointTags[(i + 1) % N]))
    return LineTags
############################### CREAR LINEAS ##############################

############################### PAREDES ##############################
InnerGripperHeight = (Constants.GripperWidth - Constants.WallThickness) / np.cos(Constants.Theta)
Phi = np.arctan2(Constants.GripperWidth - Constants.WallThickness, InnerGripperHeight)

P0 = factory.addPoint(Constants.GripperWidth - Constants.WallThickness, 0, 0)
P1 = factory.addPoint(Constants.GripperWidth, 0, 0)
P2 = factory.addPoint(Constants.WallThickness, Constants.GripperHeight + Constants.GripperHeightGift, 0)
P3 = factory.addPoint(0, Constants.GripperHeight + Constants.GripperHeightGift, 0)
P4 = factory.addPoint(0, InnerGripperHeight, 0)
PointTags = [P0, P1, P2, P3, P4]

PointTags_exterior = PointTags.copy()
############################### PAREDES ##############################

############################### Soporte ##############################
soporte1 = factory.addPoint(Constants.GripperWidth, -10, 0)
soporte2 = factory.addPoint(Constants.GripperWidth - 6, -10, 0)
soporte3 = factory.addPoint(Constants.GripperWidth - 6, -7, 0)
soporte4 = factory.addPoint(Constants.GripperWidth - 3, -7, 0)
soporte5 = factory.addPoint(Constants.GripperWidth - 3, -3, 0)
soporte6 = factory.addPoint(0, -3, 0)
soporte7 = factory.addPoint(0, 0, 0)

point_tag_soporte = [P1, soporte1, soporte2, soporte3, soporte4, soporte5, soporte6, soporte7, P0]
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
BarPositions = np.linspace(0, InnerGripperHeight, Constants.NBars + 2)
for BarPosition in BarPositions[1:-1]:
    print(f"BarPosition:{BarPosition}")
    StepWidth = 0.1
    BarTotalLength = np.tan(Phi) * BarPosition

    BarTopLength = np.tan(Phi) * (BarPosition - Constants.BarHeightThin / 2)
    BarBottomLength = np.tan(Phi) * (BarPosition + Constants.BarHeightThin / 2)
    if BarTotalLength < Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P3Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)

        PointTags += [P0Bar, P1Bar, P2Bar, P3Bar]

    if BarTotalLength > Constants.BarThinLength:
        P0Bar = factory.addPoint(BarTopLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P1Bar = factory.addPoint(BarTopLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition - Constants.BarHeightThin / 2), 0)
        P2Bar = factory.addPoint(BarTopLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P3Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition - Constants.BarHeightThick / 2), 0)
        P4Bar = factory.addPoint(0, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P5Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength - StepWidth, InnerGripperHeight - (BarPosition + Constants.BarHeightThick / 2), 0)
        P6Bar = factory.addPoint(BarBottomLength - Constants.BarThinLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        P7Bar = factory.addPoint(BarBottomLength, InnerGripperHeight - (BarPosition + Constants.BarHeightThin / 2), 0)
        PointTags += [P0Bar, P1Bar, P2Bar, P3Bar, P4Bar, P5Bar, P6Bar, P7Bar]
############################### BARRAS INTERNAS ##############################

############################### LINEAS 2D Y SUP ##############################
LineTags = addLines(PointTags)
LineTags_soporte = addLines(point_tag_soporte)
Line_tags_exterior = addLines(PointTags_exterior)

WireTag = factory.addWire(LineTags)
WireTag_soporte = factory.addWire(LineTags_soporte)
WireTag_exterior = factory.addWire(Line_tags_exterior)

SurfaceDimTag = (2, factory.addPlaneSurface([WireTag]))
SurfaceDimTag_soporte = (2, factory.addPlaneSurface([WireTag_soporte]))
SurfaceDimTag_exterior = (2, factory.addPlaneSurface([WireTag_exterior]))
############################### LINEAS 2D Y SUP ##############################

############################### LE DA SUPERFICIE ##############################
ExtrudeOut = factory.extrude([SurfaceDimTag], 0, 0, Constants.Depth)
ExtrudeOut_soporte = factory.extrude([SurfaceDimTag_soporte], 0, 0, Constants.Depth + Constants.borde)
ExtrudeOut_exterior = factory.extrude([SurfaceDimTag_exterior], 0, 0, Constants.Depth + Constants.borde)

HalfDimTag = ExtrudeOut[1]
HalfDimTag_soporte = ExtrudeOut_soporte[1]
HalfDimTag_exterior = ExtrudeOut_exterior[1]
############################### LE DA SUPERFICIE ##############################

############################### OPERACIÓN DE CORTE EN LA MITAD IZQUIERDA ##############################
# Realizar el corte en la mitad izquierda con los cilindros de la grilla
cut_result_izquierda = factory.cut([HalfDimTag], cilindros_grilla)
if cut_result_izquierda[0]:
    HalfDimTag_cortada = cut_result_izquierda[0][0]
    print("Mitad izquierda cortada:", HalfDimTag_cortada)
else:
    print("Error: No se crearon entidades durante el corte en la mitad izquierda.")

# Sincronizar después del corte
factory.synchronize()
############################### OPERACIÓN DE CORTE EN LA MITAD IZQUIERDA ##############################

############################### CILINDRO EN EL CENTRO PARA LA MITAD IZQUIERDA ##############################
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

# Realizar el corte con el cilindro central en la mitad izquierda
cut_result_cilindro_izquierda = factory.cut([HalfDimTag_cortada], [(3, cilindro_central_tag)])
if cut_result_cilindro_izquierda[0]:
    HalfDimTag_cortada = cut_result_cilindro_izquierda[0][0]
    print("Mitad izquierda con hueco para el cable:", HalfDimTag_cortada)
else:
    print("Error: No se creó ninguna entidad durante el corte con el cilindro central en la mitad izquierda.")

# Sincronizar después del corte
factory.synchronize()
############################### CILINDRO EN EL CENTRO PARA LA MITAD IZQUIERDA ##############################

############################### EXPORTAR LA MITAD IZQUIERDA ##############################
# Generar la malla para la mitad izquierda
gmsh.model.mesh.generate(3)

# Exportar la mitad izquierda
gmsh.write("FinRay_mitad_izquierda.stl")

# Limpiar la malla
gmsh.model.mesh.clear()
############################### EXPORTAR LA MITAD IZQUIERDA ##############################

############################### CREAR Y EXPORTAR LA MITAD DERECHA ##############################
# Copiar y simetrizar la garra para obtener la mitad derecha
CopyDimTags_derecha = factory.copy([HalfDimTag])
factory.synchronize()
factory.symmetrize(CopyDimTags_derecha, 1, 0, 0, 0)

# Realizar el corte con los cilindros de la grilla en la mitad derecha
cut_result_derecha = factory.cut(CopyDimTags_derecha, cilindros_grilla)
if cut_result_derecha[0]:
    HalfDimTag_derecha_cortada = cut_result_derecha[0][0]
    print("Mitad derecha cortada:", HalfDimTag_derecha_cortada)
else:
    print("Error: No se crearon entidades durante el corte en la mitad derecha.")

# Sincronizar después del corte
factory.synchronize()

# Realizar el corte con el cilindro central en la mitad derecha
cut_result_cilindro_derecha = factory.cut([HalfDimTag_derecha_cortada], [(3, cilindro_central_tag)])
if cut_result_cilindro_derecha[0]:
    HalfDimTag_derecha_cortada = cut_result_cilindro_derecha[0][0]
    print("Mitad derecha con hueco para el cable:", HalfDimTag_derecha_cortada)
else:
    print("Error: No se creó ninguna entidad durante el corte con el cilindro central en la mitad derecha.")

# Sincronizar después del corte
factory.synchronize()

# Generar la malla para la mitad derecha
gmsh.model.mesh.generate(3)

# Exportar la mitad derecha
gmsh.write("FinRay_mitad_derecha.stl")

# Limpiar la malla
gmsh.model.mesh.clear()
############################### CREAR Y EXPORTAR LA MITAD DERECHA ##############################

############################### EXPORTAR EN FORMATO STEP (OPCIONAL) ##############################
# Si deseas exportar en formato STEP, puedes hacerlo de la siguiente manera:

# Exportar la mitad izquierda en STEP
gmsh.write("FinRay_mitad_izquierda.step")

# Exportar la mitad derecha en STEP
gmsh.write("FinRay_mitad_derecha.step")
############################### EXPORTAR EN FORMATO STEP (OPCIONAL) ##############################

# Finalizar Gmsh
gmsh.finalize()
