from traceback import print_tb
import pymongo  # SE IMPORTA MONGODB
from tomlkit import datetime, document 
import datetime
from prettytable import PrettyTable

MONGO_HOST = "localhost"     # se indica el nombre del host de la base de mongodb
MONGO_PUERTO = "27017"       # se indica el puerto del host de la base de mongodb
MONGO_TIEMPO_FUERA = 1000    # se indican 1000 milisegundos

MONGO_URI = "mongodb://"+ MONGO_HOST + ":" + MONGO_PUERTO + "/"      #es la concatenacion de las variables anteriores para acceder al servidor de MongoDB que tenemos instalado

try:
    cliente = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS= MONGO_TIEMPO_FUERA)
    cliente.server_info()
    print(" ")
    print("CONEXION A MongoDB EXITOSA")   # CONFIGURACION PARA INDICAR QUE LA CONEXION FUE EXITOSA
    print("BASE DE DATOS CONECTADA")
    #cliente.close()
except pymongo.errors.ServerSelectionTimeoutError as errorTiempo:
    print("Tiempo Excedido")
except pymongo.errors.ConnectionFailure as errorConexion:
    print("Fallo al conectarse a mongodb" + errorConexion)


# Base de Datos Hotel
base = cliente["hotel"]

# Coleccion Registros
coleccion = base["registros"]

# Coleccion Encargados y Administradores
colEncargados = base["Encargados"]


# ASIGNAR HABITACIONES A PASAJEROS
def asignarHabitacion():
    myTable = PrettyTable(["id_habitacion","num_habitacion", "capacidad","orientacion","disponible"])
    pasajerosIngreso =[]
    contadorPasajeros = 0
    habitacionesCapacidad = []
    rutPasajero = ""
    nombrePasajero =""
    apellidoPasajero =""
    fechaReserva=""
    numeroPasajeros = int(input("Ingrese el numero de pasajeros para Asignar una Habitacion disponible \n"))
    data = coleccion.find({"capacidad":numeroPasajeros})
    for habitacion in data : 
            if  habitacion["disponible"] == True :
                habitacionesCapacidad.append(habitacion)
                myTable.add_row([habitacion["id_habitacion"],habitacion["numero_habitacion"], habitacion["capacidad"], habitacion["orientacion"], habitacion["disponible"]])
    
    if len(habitacionesCapacidad) == 0:
        print("No hay habitaciones disponibles. Ingrese otro numero de pasajeros")
        asignarHabitacion()  

    print(myTable)
    if habitacionesCapacidad != []:
            habitacionElegida = int(input("Indique el numero de la habitacion que desea reservar \n"))
            for disponible in habitacionesCapacidad:                       
                        if habitacionElegida == disponible["numero_habitacion"]:
                            print(f"Para confirmar la habitacion numero {habitacionElegida} ingrese 'si' y Para cancelar ingrese 'no'")
                            confirmar = input()
                            if confirmar == "si":
                                while contadorPasajeros < numeroPasajeros:
                                    contadorPasajeros +=1
                                    print(f"Ingrese Rut del Pasajero {contadorPasajeros}")
                                    rutPasajero = input()
                                    print(f"Ingrese Nombre del Pasajero {contadorPasajeros}")
                                    nombrePasajero = input() 
                                    print(f"Ingrese Apellido del Pasajero {contadorPasajeros}")
                                    apellidoPasajero = input()                                   
                                    print(rutPasajero, nombrePasajero, apellidoPasajero)
                                    pasajeroIngreso = {
                                        "rut": rutPasajero,
                                        "nombre":nombrePasajero,
                                        "apellido":apellidoPasajero
                                    }
                                    pasajerosIngreso.append(pasajeroIngreso)
                                   
                                fechaReserva = input("ingrese fecha ej:YYYY-MM-DD \n")
                            else:
                                asignarHabitacion()
            print(pasajerosIngreso)
            dataHabitacion = coleccion.find_one({"id_habitacion":habitacionElegida})
            if dataHabitacion["registro_reservas"] == []:
                n_registro = 1
            else:
                nmayor = 0
                for data in dataHabitacion["registro_reservas"]:
                    if data["id_registro"] > nmayor:
                        nmayor = data["id_registro"]
                n_registro = nmayor +1

            dataHabitacion["registro_reservas"].append({
                "id_registro":n_registro,
                "fecha_reserva": fechaReserva,
                "pasajeros":pasajerosIngreso
            })
            coleccion.update_one({"id_habitacion":habitacionElegida},{"$set":{"registro_reservas":dataHabitacion["registro_reservas"]}})
            coleccion.update_one({"id_habitacion":habitacionElegida},{"$set":{"disponible":False}})
            print("Habitacion reservada con exito")


# CREAR HABITACIONES
def IngresarHabitacion():
    id_habitacion = int(input("ingrese id de la habitacion que desea agregar: "))  
    num_habitacion  = int(input("ingrese numero de la habitacion que desea agregar: "))
    capacidad = int(input("ingrese capacidad de pasajeros que puede contener la habitacion: "))
    orientacion = str(input("ingrese orientacion de la habitacion: "))
    diccionario = { "id_habitacion": id_habitacion, "numero_habitacion": num_habitacion, "capacidad": capacidad, "orientacion": orientacion, "disponible":True, "registro_reservas":[]}
    coleccion.insert_one(diccionario)
    print("Cargando...")
    print("Habitacion Creada con Exito")


# MOSTRAR HABITACIONES EN TABLA
def MostrarHabitaciones():
    myTable = PrettyTable(["id_habitacion","num_habitacion", "capacidad","orientacion","disponible"])
    for x in coleccion.find():
        for documento in coleccion.find(x): 
            id_habitacion = documento["id_habitacion"]
            num_habitacion = documento["numero_habitacion"]
            capacidad = documento["capacidad"]
            orientacion = documento["orientacion"]
            disponible = documento["disponible"]
        myTable.add_row([id_habitacion, num_habitacion, capacidad, orientacion, disponible])
    return myTable


def historialRegistro():
    MostrarHabitaciones()
    print("Ingrese el id de la habitacion para ver su historial de registros")
    nHabitacion = int(input())
    historial = coleccion.find_one({"id_habitacion":nHabitacion})
    myTable =PrettyTable(["id_registro", "fecha_reserva", "pasajeros"])
    if historial["registro_reservas"] != []:
        for reg in historial["registro_reservas"]:
            id_registro = reg["id_registro"]
            fecha_reserva = reg["fecha_reserva"]
            pasajeros = len(reg["pasajeros"])
            myTable.add_row([id_registro,fecha_reserva,pasajeros])
        print(myTable)
        verPasajeros = int(input("Ingresa el ID del registro para ver informacion de pasajeros \n"))
        myTable2 =PrettyTable(["rut", "nombre", "apellido"])
        if verPasajeros:
            for e in historial["registro_reservas"]:
                if e["id_registro"] == verPasajeros:
                    for pasajero in e["pasajeros"]:                  
                        rut = pasajero["rut"]
                        nombre = pasajero["nombre"]
                        apellido = pasajero["apellido"]
                        myTable2.add_row([rut,nombre,apellido])
            print(myTable2)        
    else:
        print("Esta habitacion no ha sido asignada")






# VALIDACIONES PARA SESION DE ENCARGADOS Y ADMINISTRADORES PARA SUS RESPECTIVOS MENUS
def ValidacionEncargadosAdmin():
    bucleEncargados = 0
    while bucleEncargados == 0:
        nom_user = str(input("Ingrese su nombre de usuario: "))
        diccionarioBuscado = colEncargados.find_one({"nickname": nom_user})
        claveIngresada = str(input("Ingrese la clave de su sesion: "))
        for documento in diccionarioBuscado:
            nick = diccionarioBuscado["nickname"]
            clave = diccionarioBuscado["clave"]
            tipo_user = diccionarioBuscado["tipo_usuario"]
            if (nick == nom_user) and (clave == claveIngresada):
                print(" ")
                print("Usuario Verificado")
                print("Has Ingresado a la Sesion")
                if tipo_user == "Encargado":
                    print(" ")
                    print("MENU ENCARGADO DE HOTEL: ")
                    print(MenuEncargados())
                    bucleEncargados = 1
                elif tipo_user == "Administrador":
                    print(" ")
                    print("Menu Administrador")
                    print(MenuAdmin())
                    bucleEncargados = 1          
                else:
                    print("Tipo de Usuario Incorrecto")

                break
            else:
                print(" ")
                print("Usuario o contraseña incorrecta")
    return " "


# MENU DE ENCARGADOS
def MenuEncargados():

    menuEncargado = 0
    while menuEncargado == 0:
        print(" ")
        print("***************************************************")
        print("MENU HOTEL")
        print("1 : Mostrar Habitaciones")
        print("2 : Crear Habitaciones")
        print("3 : Asignar habitaciones a Pasajeros")
        print("4 : Mostrar Historial de Registros")
        print("5 : SALIR")
        print("***************************************************")
        print(" ")
        ctrl = input("Ingrese el numero de la opcion que desea realizar: ")
        if ctrl == "1":
            print("Usted ha escogido la opcion: Mostrar Habitaciones")
            print(MostrarHabitaciones())
        elif ctrl == "2":
            print("Usted ha escogido la opcion: Crear Habitaciones")
            print(IngresarHabitacion())
        elif ctrl == "3":
            print("Usted ha escogido la opcion: Asignar habitaciones a Pasajeros")
            print(asignarHabitacion())
        elif ctrl == "4":
            print("Usted ha escogido la opcion: Mostrar Historial de Registros")
            print(historialRegistro())    
        elif ctrl == "5":
            print("Usted ha escogido la opcion: SALIR")
            menuEncargado = 1
        else:
            print("")
            print ("> Ingrese una opcion valida del MENU <")
            print("") 
        
    print("")
    print("Saliendo...")
    print("*")
    return " "


# MENU DE ADMINISTRADOR
def MenuAdmin():

    menuAdmin = 0
    while menuAdmin == 0:
        print(" ")
        print("***************************************************")
        print("MENU ADMINISTRADOR")
        print("1 : Crear usuarios Encargados de Hotel")
        print("2 : Eliminar usuarios Encargados de Hotel")
        print("3 : Actualizar usuarios Encargados de Hotel")
        print("4 : Mostrar todos los usuarios creados (Encargados y Administradores)")
        print("5 : SALIR")
        print("***************************************************")
        print(" ")
        ctrl = input("Ingrese el numero de la opcion que desea realizar: ")
        if ctrl == "1":
            print("Usted ha escogido la opcion: Crear usuarios Encargados de Hotel")
            print(CrearEncargadosHotel())
        elif ctrl == "2":
            print("Usted ha escogido la opcion: Eliminar usuarios Encargados de Hotel")
            print(EliminarEncargadosAdmin())
        elif ctrl == "3":
            print("Usted ha escogido la opcion: Actualizar usuarios Encargados de Hotel")
            print(ActualizarEncargadosAdmin())
        elif ctrl == "4":
            print("Usted ha escogido la opcion: Mostrar todos los usuarios creados (Encargados y Administradores)")
            print(MostrarEncargadosAdmin())
        elif ctrl == "5":
            print("Usted ha escogido la opcion: SALIR")
            menuAdmin = 1
        else:
            print("")
            print ("> Ingrese una opcion valida del MENU <")
            print("") 
        
    print("")
    print("Saliendo...")
    print("*")
    return " "


# CREAR ENCARGADOS Y ADMINISTRADORES
def CrearEncargadosHotel():
    id_usuario = int(input("ingrese id del usuario que desea agregar: "))
    print("Ingrese Nombre Completo del usuario a crear:")
    primer_nombre = str(input("Ingrese Primer nombre: "))   
    segundo_nombre  = str(input("Ingrese Segundo nombre: "))
    primer_apellido = str(input("Ingrese Primer Apellido: "))
    segundo_apellido = str(input("Ingrese Segundo Apellido: "))
    print("Ingrese Tipo de Usuario a Crear")
    tipo_usuario = str(input("Encargado o Administrador: "))

    validacion = 0
    while validacion == 0:
        if tipo_usuario != "Encargado" and tipo_usuario != "Administrador":
            print("Ingrese Correctamente el Tipo de Usuario a Crear:")
            tipo_usuario = str(input("Encargado o Administrador: "))
        else:
            print("Tipo de Usuario Ingresado Correctamente")
            validacion = 1

    nom_user = str(input("Ingrese un nombre de Usuario para esta persona: "))
    clave_cuenta = str(input("Ingrese una contraseña de Usuario para esta persona: "))
    diccionario = { "id_usuario": id_usuario, "primer_nombre": primer_nombre, "segundo_nombre": segundo_nombre, "primer_apellido": primer_apellido, "segundo_apellido": segundo_apellido, "tipo_usuario": tipo_usuario, "nickname": nom_user, "clave": clave_cuenta}
    x = colEncargados.insert_one(diccionario)
    print(" ")
    return "USUARIO CREADO"


# ELIMINAR ENCARGADOS Y ADMINISTRADORES
def EliminarEncargadosAdmin():
    nom_user = str(input("Ingrese el nombre de Usuario que desea eliminar: "))
    x = colEncargados.delete_one({"nickname": nom_user})
    print(" ")
    return "USUARIO ELIMINADO"


# ACTUALIZAR ENCARGADOS Y ADMINISTRADORES
def ActualizarEncargadosAdmin():
    nom_user = str(input("Ingrese el nombre de Usuario que desea Actualizar: "))
    print("Que Atributo Desea Cambiar para esta Cuenta")
    print("Opcion 1: Primer Nombre")
    print("Opcion 2: Segundo Nombre")
    print("Opcion 3: Primer Apellido")
    print("Opcion 4: Segundo Apellido")
    print("Opcion 5: Tipo de Usuario")
    print("Opcion 6: Contraseña")
    print("Opcion 7: Nombre de Usuario")
    print("")
    nombre_campo = int(input("seleccione el numero de la opcion que desea actualizar: "))
    if nombre_campo == 1:
        campo_cambiar = "primer_nombre"
    elif nombre_campo == 2:
        campo_cambiar = "segundo_nombre"
    elif nombre_campo == 3:
        campo_cambiar = "primer_apellido"
    elif nombre_campo == 4:
        campo_cambiar = "segundo_apellido"
    elif nombre_campo == 5:
        campo_cambiar = "tipo_usuario"
    elif nombre_campo == 6:
        campo_cambiar = "clave"
    elif nombre_campo == 7:
        campo_cambiar = "nickname"
    else:
        print("Ingrese una Opcion Valida")
    
    valor_nuevo = input("Ingrese Valor que desea ingresar: ")

    x = colEncargados.update_one({"nickname": nom_user}, {"$set": {campo_cambiar: valor_nuevo} })
    print(" ")
    return "USUARIO ACTUALIZADO"


# MOSTRAR TODOS LOS ENCARGADOS Y ADMINISTRADORES
def MostrarEncargadosAdmin():
    myTable = PrettyTable(["ID Usuario", "Primer Nombre", "Segundo Nombre", "Primer Apellido","Segundo Apellido", "Tipo usuario", "Contraseña", "Nombre de Usuario"])
    for x in colEncargados.find():
        for documento in colEncargados.find(x): 
            id_usuario = documento["id_usuario"]
            primer_nombre = documento["primer_nombre"]
            segundo_nombre = documento["segundo_nombre"]
            primer_apellido = documento["primer_apellido"]
            segundo_apellido = documento["segundo_apellido"]
            tipo_usuario = documento["tipo_usuario"]
            clave = documento["clave"]
            nickname = documento["nickname"]

        myTable.add_row([ id_usuario, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, tipo_usuario, clave, nickname])
    return myTable



sistema = 0

while sistema == 0:
    print(" ")
    print("***************************************************")
    print("BIENVENIDOS AL SISTEMA")
    print("HOTEL DUERME BIEN")
    print(" ")
    print(" ")
    print("1 : Ingresar al Sistema")
    print("2 : SALIR")
    print(" ")
    print(" ")
    print("***************************************************")
    print(" ")
    opcion = input("Ingrese el numero de la opcion que desea realizar: ")
    if opcion == "1":
        print("Usted ha escogido la opcion: Ingresar al Sistema")
        print(" ")
        print("***************************************************")
        print("BIENVENIDOS AL SISTEMA")
        print("HOTEL DUERME BIEN")
        print(" ")
        print(" ")
        print("Ingrese su usuario y Contraseña para Iniciar su Sesion")
        print(" ")
        print(" ")
        print("***************************************************")
        print(" ")
        print(ValidacionEncargadosAdmin()) 
    elif opcion == "2":
        print("Usted ha escogido la opcion: SALIR")
        sistema = 1
    else:
        print("")
        print ("> Ingrese una opcion valida del MENU <")
        print("") 
    
print("")
print("Cerrando Sesion...")
print("*")



