# -*- encoding: utf-8 -*-
from .models import Barca, Reserva, Control, PuntoVenta, TipoBarca
from datetime import datetime, timedelta
import json, urllib
from django.http import HttpResponse
import time

#Devuelve el numero de la reserva, el punto de venta. La hora estimada a 0
def reserva(request, tipo, PV):
	nombreTipo = ""
	if tipo == "1":
		nombreTipo = "rio"
	elif tipo == "2":
		nombreTipo = "barca"
	else:
		nombreTipo = "gold"

	# se recupera en numero de reserva desde la tabla control
	registro_control = Control.objects.all()[0]
	print '-------registro_control------'; print registro_control.num_reserva_rio; print '-----------'

	if tipo == "1":
		numero = registro_control.num_reserva_rio
		registro_control.num_reserva_rio += 1

	elif tipo == "2":
		numero = registro_control.num_reserva_electrica
		registro_control.num_reserva_electrica += 1

	elif tipo == "3":
		numero = registro_control.num_reserva_gold
		registro_control.num_reserva_gold += 1

	punto_venta = PuntoVenta.objects.get(codigo = PV)

	print '-------punto_venta------'; print punto_venta.nombre; print '-----------'
	print '---- numero reserva----';print numero; print '-------'
	t_barca = TipoBarca.objects.get(codigo = tipo)
	print '-------tipo_barca------'; print t_barca.tipo; print '-----------'

	# SE METE EL REGISTRO EN LA TABLA DE RESERVAS
	registro_reserva = Reserva(numero = numero,
							   punto_venta = punto_venta,
							   tipo_barca = t_barca,
							   hora_reserva = (datetime.now() + timedelta(hours = 2)).isoformat(),
							   #hora_reserva = datetime.strftime(datetime.now() + timedelta(hours = 2), "%H:%M:%S"),
							   hora_prevista = (datetime.now() + timedelta(hours = 2)).isoformat(),
							   fuera = False)

	reservas = [0,0,0]
	data = {}
	reservas[int(tipo)-1] = numero
	print '-------AQUI  LLEGA 2------'
	try:
		print '-------AQUI  LLEGA 3------'
		registro_reserva.save()
		print '-------AQUI  LLEGA 4------'
		registro_control.save()
		print '-------AQUI  LLEGA 5------'

		#data = {'exito' : 1, 'PV' : punto_venta.nombre, 'numero' : reservas}
		data = {'reservas' : reservas, 'exito' : nombreTipo, 'hora reserva' : datetime.strftime(datetime.now(), "%H:%M:%S") , 'hora prevista' : datetime.strftime(datetime.now(), "%H:%M:%S"), 'PV' : registro_reserva.punto_venta.nombre, 'error' : 'no'}
		print 'AQUI TAMBIEN'
	except Exception, e:
		data = {'exito':0, 'error': 'si', 'descripcion' : e}

	return HttpResponse(json.dumps(data), 'application/json')

#Devuelve el numero de la reserva, el punto de venta y la hora estimada de salida de la barca resevada
def reservaAntigua(request, tipo, PV): # tipo 1|2|3|4 segun el tipo de barca
	#	RECOGE EL TIPO DE BARCA Y ACTUALIZA LA BDD CON LA SALIDA DE ESA BARCA
	# Busca las primeras barcas libres para escoger la que nos pide
	url = "http://losbarkitos.herokuapp.com/primera_libre/"
	respuesta = urllib.urlopen(url)
	print 'respuesta'; print respuesta
	# Contiene un JSON con las primeras barcas que llegan segun el tipo
	# [0] - rio
	# [1] - electrica
	# [2] - whaly
	# [3] - gold
	nombreTipo = ""
	if tipo == "1":
		nombreTipo = "rio"
	elif tipo == "2":
		nombreTipo = "barca"
	else:
		nombreTipo = "gold"

	print "nombre Tipo: ";print nombreTipo; print "------"
	try:
		json_data = json.load(respuesta)
	except Exception, e:
		print "Error e = %s" % e

	print '------json_data------';print json_data; print '-----------'; print json_data[nombreTipo]["libre"]

	barca = Barca.objects.get(nombre = json_data[nombreTipo]["nombre"])
	print '-------barca------'; print barca; print '-----------'

	try:
		h_prevista = barca.libre
		h_prevista = datetime.strftime(barca.libre, "%H:%M:%S")
	except Exception, e:
		h_prevista = barca.libre
		raise e
	if h_prevista == None: # Hay barcas disponibles, y la h_prevista = actual
		h_prevista = (datetime.now() + timedelta(hours = 2))
		h_prevista = datetime.strftime(datetime.now() + timedelta(hours = 2), "%H:%M:%S")

	print '-------h_prevista------'; print h_prevista; print '-----------'

	barca.control += 1 # barca una vuelta mas
	if barca.libre == None: # Barca disponible
		barca.libre = (datetime.now() + timedelta(hours = 3)).isoformat()
	else:
		barca.libre = (barca.libre + timedelta(hours = 1)).isoformat()
	print '-------barca.libre------'; print barca.libre; print '-----------'

	# se recupera en numero de reserva desde la tabla control
	registro_control = Control.objects.all()[0]
	print '-------registro_control------'; print registro_control.num_reserva_rio; print '-----------'

	if tipo == "1":
		numero = registro_control.num_reserva_rio
		registro_control.num_reserva_rio += 1

	elif tipo == "2":
		numero = registro_control.num_reserva_electrica
		registro_control.num_reserva_electrica += 1

	elif tipo == "3":
		numero = registro_control.num_reserva_gold
		registro_control.num_reserva_gold += 1

	punto_venta = PuntoVenta.objects.get(codigo = PV)
	print '-------punto_venta------'; print punto_venta.nombre; print '-----------'
	print '---- numero reserva----';print numero; print '-------'
	t_barca = TipoBarca.objects.get(codigo = tipo)
	print '-------tipo_barca------'; print t_barca.tipo; print '-----------'

	# SE METE EL REGISTRO EN LA TABLA DE RESERVAS
	registro_reserva = Reserva(numero = numero,
							   punto_venta = punto_venta,
							   tipo_barca = t_barca,
							   hora_reserva = (datetime.now() + timedelta(hours = 2)).isoformat(),
							   #hora_reserva = datetime.strftime(datetime.now() + timedelta(hours = 2), "%H:%M:%S"),
							   hora_prevista = h_prevista.isoformat(),
							   fuera = False)

	print '-------AQUI  LLEGA 1------'; print barca; print '-----------'
	reservas = [0,0,0]
	data = {}
	reservas[int(tipo)-1] = numero
	print '-------AQUI  LLEGA 2------'
	try:
		barca.save()
		print '-------AQUI  LLEGA 3------'
		registro_reserva.save()
		print '-------AQUI  LLEGA 4------'
		registro_control.save()
		print '-------AQUI  LLEGA 5------'

		#data = {'exito' : 1, 'PV' : punto_venta.nombre, 'numero' : reservas}
		data = {'reservas' : reservas, 'exito' : nombreTipo, 'hora reserva' : datetime.strftime(datetime.now(), "%H:%M:%S") , 'hora prevista' : datetime.strftime(h_prevista, "%H:%M:%S"), 'PV' : registro_reserva.punto_venta.nombre, 'error' : 'no'}
		print 'AQUI TAMBIEN'
	except :
		data = {'exito':0, 'error': 'si'}

	return HttpResponse(json.dumps(data), 'application/json')


# Se marca la reserva como fuera y se actualizan los horarios.
# Responde a la llamada del boton de salida de la pantalla de control
def reserva_fuera(request, tipo, numero):

	TB = TipoBarca.objects.get(codigo = tipo)
	try:
		reserva = Reserva.objects.get(tipo_barca = TB, numero = numero, fuera = False)
	except Reserva.DoesNotExist:
		data = {'exito' : 0, 'error' : 'Esta reserva no existe'}
		return HttpResponse(json.dumps(data), 'application/json')

	# se marca la reserva como salida
	reserva.fuera = True
	reserva.save()

	barca = reserva.tipo_barca
	#print barca

	# llamamos salida barca para hacer efectiva la salida de la barca
	#url = 'http://losbarkitos.herokuapp.com/salida/%s' % tipo
	#respuesta = urllib.urlopen(url)
	#json_data = json.loads(respuesta.read())

	data = {'tipo' : tipo, 'numero' : numero}

	return HttpResponse(json.dumps(data), 'application/json')

def listadoReservas(request, tipo):

	tipo_barca = 0
	if tipo == "Rio":
		tipo_barca = 1
	elif tipo == "Electrica":
		tipo_barca = 2
	elif tipo == "Whaly":
		tipo_barca = 3
	elif tipo == "Gold":
		tipo_barca = 4

	TB = TipoBarca.objects.get(codigo = tipo_barca)

	try:
		reservas = Reserva.objects.filter(tipo_barca = TB, fuera = 0)
		#print 'Reservas : ';print reservas; print '-------'
	except Reserva.DoesNotExist:
		data = {'error' : 'si'}
		return HttpResponse(json.dumps(data), 'application/json')

	dict_data = {}
	for reserva in reservas:
		data = {'numero' : reserva.numero, 'tipo' : tipo_barca, 'base' : reserva.punto_venta.nombre, 'hora_reserva' : datetime.strftime(reserva.hora_reserva, "%H:%M:%S"), 'hora_prevista' : datetime.strftime(reserva.hora_prevista, "%H:%M:%S"), 'fuera' : reserva.fuera}
		dict_data[str(reserva.numero)] = data

	dict_data['error'] = 'no'
	return HttpResponse(json.dumps(dict_data), 'application/json')

def posibleReserva(request):
#si el numero de reserva en control es -1, no se puede reservar
	control = Control.objects.all()[0]
	respuesta = [True, True, True, True]
	if control.num_reserva_rio == -1:
		respuesta[0] = False
	if control.num_reserva_electrica == -1:
		respuesta[1] = False
	if control.num_reserva_whaly == -1:
		respuesta[2] = False
	if control.num_reserva_gold == -1:
		respuesta[3] = False

	return HttpResponse(json.dumps(respuesta), 'application/json')

def cierreDia(request):
	try:
		# pongo las reservas a 0
		control = Control.objects.all()[0]

		control.num_reserva_rio = 1
		control.num_reserva_electrica = 1
		control.num_reserva_whaly = 1
		control.num_reserva_gold = 1

		control.save()
		# Las Barcas las inicializo
		barcas = Barca.objects.all()

		for barca in barcas:
			barca.libre = None
			barca.control = 0
			barca.navegando = 0
			barca.llegada_base = None
			barca.save()

		# elimino las reservas
		reservas = Reserva.objects.all()
		reservas.delete()

		respuesta = 'ok'
		

	except Exception, e:
		respuesta = "Error en el procesamiento : %s" % e

	datos = {'mensaje' : respuesta}
	return HttpResponse(json.dumps(datos), 'application/json')	

def barcasDia(request):
	try:
		# pongo las reservas a 0
		control = Control.objects.all()[0]
		total = [control.num_reserva_rio, control.num_reserva_electrica, control.num_reserva_gold]		
		respuesta = "ok"
		datos = {'mensaje' : respuesta, 'contenido' : total}


	except Exception, e:
		respuesta = "Error en el procesamiento : %s" % e
		datos = {'mensaje' : 'ko', 'contenido' : respuesta}

	return HttpResponse(json.dumps(datos), 'application/json')	

def totalReservas(request):
	try:
		rio = TipoBarca.objects.get(codigo = 1)
		electrica = TipoBarca.objects.get(codigo = 2)
		whaly = TipoBarca.objects.get(codigo = 3)
		gold = TipoBarca.objects.get(codigo = 4)

		num_reservas_rio = Reserva.objects.filter(tipo_barca = rio, fuera = 0).count()
		num_reservas_electrica = Reserva.objects.filter(tipo_barca = electrica, fuera = 0).count()
		num_reservas_whaly = Reserva.objects.filter(tipo_barca = whaly, fuera = 0).count()
		num_reservas_gold = Reserva.objects.filter(tipo_barca = gold, fuera = 0).count()

		res = {'rio' : str(num_reservas_rio), 'electrica' : str(num_reservas_electrica), 'whaly' : str(num_reservas_whaly), 'gold' : str(num_reservas_gold)} 
		datos = {'mensaje' : 'OK', 'contenido' : res}
	except:
		datos = {'mensaje' : 'KO'}

	return HttpResponse(json.dumps(datos), 'application/json')

def incrementarReserva(request, tipo):
	control = Control.objects.all()[0]
	if int(tipo) == 1: # RIO
		control.num_reserva_rio += 1
	elif int(tipo) == 2: # BARCA
		control.num_reserva_electrica += 1
	elif int(tipo) == 3: # GOLD
		control.num_reserva_gold += 1

	control.save()

	respuesta = [control.num_reserva_rio, control.num_reserva_electrica, control.num_reserva_gold]
	datos = {'mensaje' : 'ok', 'contenido' : respuesta}

	return HttpResponse(json.dumps(datos), 'application/json')
