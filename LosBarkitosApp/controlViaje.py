# -*- encoding: utf-8 -*-
# funciones para el control del tickets CEPORRO
from django.http import HttpResponse
from .models import Viaje, PuntoVenta, TipoBarca, Vendedor, Control, Barca
from datetime import datetime
from datetime import timedelta
import MySQLdb
import datetime
import json, time
from django.core.serializers.json import DjangoJSONEncoder
from random import randint, seed
#from django.db import transaction


# Se tiene que insertar un registro en la base de datos Viaje.
# Hay que tener en cuenta que el numero sale de Control y se
# tiene que incrementar este numero y volverlo a grabar
#@transaction.commit_manually
def registroBarca(request, ticket, tipo, precio, pv, vend, blanc):

	regPV = PuntoVenta.objects.get(codigo = pv)
	regBarca = TipoBarca.objects.get(codigo = tipo)
	regVendedor = Vendedor.objects.get(codigo = vend)

	if ticket == "0":
		blanc = "0"

	# a lo bestia
	if blanc == "1":
		#print ' ENTRA EN BLANCO'
		reg = Viaje(numero 		= ticket,
					precio 		= precio,
					fecha 		= datetime.datetime.now() + datetime.timedelta(hours = 2),
					punto_venta = regPV,
					barca 		= regBarca,
					vendedor 	= regVendedor,
					blanco		= 1)
	else:
		#print 'ENTRA EN NEGRO '
		reg = Viaje(numero 		= ticket,
					precio 		= precio,
					fecha 		= datetime.datetime.now() + datetime.timedelta(hours = 2),
					punto_venta = regPV,
					barca 		= regBarca,
					vendedor 	= regVendedor,
					blanco		= 0)

	control = Control.objects.all()[0]
	if tipo == 1: #Barkito
		control.num_reserva_rio += 1
	elif tipo == 3: #Barca
		control.num_reserva_electrica += 1
	elif tipo == 4: #Gold
		control.num_reserva_gold +=1
	control.save()

	try:
		#transaction.commit()
		reg.save()
	except:
		#transaction.rollback()
		data = {'error' : 1, 'tipo error' : 'Error en la grabacion del viaje'}
		return HttpResponse(json.dumps(data), 'application/json')

	data = {'error' : 0 ,'Numero': ticket, 'Precio': precio, 'Tipo Barca': regBarca.tipo}

	return HttpResponse(json.dumps(data), 'application/json')

# Devuelve un listado de los viajes segun el tipo de barca (0 para todos), punto de venta, o vendedor
def listadoViajes(request, tipo, pv):
	#print 'PV - '; print pv
	#if tipo != '0':
#		filtro_tipo = TipoBarca.objects.get(codigo = tipo)
	#if pv != '0':
	#	print 'entra PV'
	#	filtro_pv = PuntoVenta.objects.get(codigo = pv)

	#if vend != '0':
#		filtro_vend = Vendedor.objects.get(codigo = vend)

	#
	#if   tipo != '0' and pv != '0' and vend != '0':
	#	viajes = Viaje.objects.filter(barca = filtro_tipo, punto_venta = filtro_pv, vendedor = filtro_vend)
	#elif tipo != '0' and pv != '0' and vend == '0':
	#	viajes = Viaje.objects.filter(barca = filtro_tipo, punto_venta = filtro_pv)
	#elif tipo != '0' and pv == '0' and vend != '0':
#		viajes = Viaje.objects.filter(barca = filtro_tipo, vendedor = filtro_vend)
	#elif tipo != '0' and pv == '0' and vend == '0':
	#	viajes = Viaje.objects.filter(barca = filtro_tipo)
	#elif tipo == '0' and pv != '0' and vend != '0':
	#	viajes = Viaje.objects.filter(punto_venta = filtro_pv, vendedor = filtro_vend)
	#elif tipo == '0' and pv != '0' and vend == '0':
	#	viajes = Viaje.objects.filter(punto_venta = filtro_pv)
	#elif tipo == '0' and pv == '0' and vend != '0':
	#	viajes = Viaje.objects.filter(vendedor = filtro_vend)
	#elif tipo == '0' and pv == '0' and vend == '0':
	#	viajes = Viaje.objects.filter(fecha__startswith = filtro_fecha.date())

	filtro_fecha = datetime.datetime.now()

	filtro_PV = PuntoVenta.objects.get(codigo = pv)
	viajes = Viaje.objects.filter(fecha__startswith = filtro_fecha.date(), punto_venta = filtro_PV).order_by('fecha')

	numBarcas = Viaje.objects.filter(punto_venta = filtro_PV, fecha__startswith = filtro_fecha.date()).count()

	dict_viaje = {}
	datos = {}
	i = 1
	for viaje in viajes:
		datos = {'numero': viaje.numero, 'fecha': datetime.datetime.strftime(viaje.fecha, "%H:%M:%S"), 'tipo':viaje.barca.tipo, 'punto_venta':viaje.punto_venta.nombre, 'nombre_vendedor':viaje.vendedor.nombre, 'precio':viaje.precio}
		dict_viaje[str(i)] = datos
		i += 1

	dict_viaje['error'] = 'no'
	dict_viaje['numero_viajes'] = numBarcas

	try:
		jsonDict = json.dumps(dict_viaje)
	except Exception, e:
		data['error'] = e.strerror

	return HttpResponse(jsonDict, 'application/json')


#ESTE METODO DEVUELVE EL NUMERO QUE HAY QUE PONER EN EL TICKET Y SU RESERVA
#@transaction.commit_manually
def ultimoNumero(request, precio_ticket):
	seed()
	aleatorio = randint(1,10)
	datos = Control.objects.get()
	num = datos.num_viaje
	#print 'num = %s' % num
	negro = datos.num_negro

	dicc = {}
	# Este es un ticket en blanco
	if aleatorio <= negro:
		dicc['error'] = 'no'
		dicc['numero'] = num
		dicc['negro'] = 'no'

		# Aumento el numero de ticket y lo grabo en la bdd
		num = num + 1
		#print 'num = %s' % num
		datos.num_viaje = num
		try:
			#transaction.commit()
			#print 'num_viaje = %s' % num
			datos.save()
		except:
			#transaction.rollback()
			data = {'error' : 'si', 'tipo error' : 'Error en la grabacion del Control de datos'}
			return HttpResponse(json.dumps(data), 'application/json')

	#ticket en negro
	else:
		# cojo un numero de ticket del mismo dia y del mismo valor 	que el ticket a sacar
		dia = datetime.datetime.now().strftime("%d")
		mes = datetime.datetime.now().strftime("%m")
		ano = datetime.datetime.now().strftime("%Y")

		db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
		cursor = db.cursor()
		llamada = 'SELECT numero from losbarkitosapp_viaje where precio=%s and year(fecha)=%s  and month(fecha)=%s and day(fecha)=%s' % (precio_ticket, ano, mes, dia)

		cursor.execute(llamada)

		NUMERO =  cursor.fetchone()
		db.close()

		if NUMERO is not None:
			# existe un ticket con el mismo valor y se puede hacer negro
			dicc['error'] = 'no'
			dicc['numero'] = NUMERO[0]
			dicc['negro'] = 'si'
		else:
			# no existe el ticket con el mismo valor y entonces tiene que ser blanco
			dicc['error'] = 'no'
			dicc['numero'] = num
			dicc['negro'] = 'no'

			# Aumento el numero de ticket y lo grabo en la bdd
			num = num + 1
			datos.num_viaje = num
			try:
				#transaction.commit()
				datos.save()
			except Exception, e:
				#transaction.rollback()

				data = {'error' : 'si', 'tipo error' : e.strerror}
				return HttpResponse(json.dumps(data), 'application/json')

	#Recupero el numero de reserva de la barca 
	reservas = [datos.num_reserva_rio, datos.num_reserva_electrica, datos.num_reserva_gold]
	dicc['reservas'] = reservas
	try:
		jsonDict = json.dumps(dicc)
	except Exception, e:
		dicc['error'] = 'si'
		dicc['descripcion error'] = e.strerror
		jsonDict = json.dumps(dicc)

	return HttpResponse(jsonDict, 'application/json')

def ajustarNumeroFalloImpresion(request, tipo):
	dicc = {}
	print tipo
	try:
		control = Control.objects.get()

		if tipo == "1":
			control.num_reserva_rio = control.num_reserva_rio - 1
		elif tipo == "2":
			control.numero_reserva_electrica = control.numero_reserva_electrica - 1
		else:
			control.numero_reserva_gold = control.numero_reserva_gold - 1

		control.num_viaje = control.num_viaje - 1
		control.save()
		dicc["error"] = "no"
	except Exception, e:
		print e.strerror
		dicc["error"] = "si"

	jsonDict = json.dumps(dicc)

	return HttpResponse(jsonDict, 'application/json')

def primeraLlegar(request):

	tipoRio 	  = TipoBarca.objects.get(codigo = 1)
	tipoElectrica = TipoBarca.objects.get(codigo = 2)
	tipoWhaly	  = TipoBarca.objects.get(codigo = 3)
	tipoGold	  = TipoBarca.objects.get(codigo = 4)

	dicc = {}

	rio 		= Barca.objects.filter(tipo_barca = tipoRio, llegada_base__isnull = False).order_by('llegada_base')
	electrica 	= Barca.objects.filter(tipo_barca = tipoElectrica, llegada_base__isnull = False).order_by('llegada_base')
	whaly	 	= Barca.objects.filter(tipo_barca = tipoWhaly, llegada_base__isnull = False).order_by('llegada_base')
	gold	 	= Barca.objects.filter(tipo_barca = tipoGold, llegada_base__isnull = False).order_by('llegada_base')

	try:
		if rio:
			dicc["rio"] = datetime.datetime.strftime(rio[0].llegada_base, "%H:%M:%S")
		else:
			dicc["rio"] = "---"
	except Exception, e:
		dicc["rio"] = "---"
	try:
		if electrica:
			dicc["electrica"] = datetime.datetime.strftime(electrica[0].llegada_base, "%H:%M:%S")
		else:
			dicc["electrica"] = "---"
	except Exception, e:
		dicc["electrica"] = "---"
	try:
		if whaly:
			dicc["whaly"] = datetime.datetime.strftime(whaly[0].llegada_base, "%H:%M:%S")
		else:
			dicc["whaly"] = "---"
	except Exception, e:
		dicc["whaly"] = "---"
	try:
		if gold:
			dicc["gold"] = datetime.datetime.strftime(gold[0].llegada_base, "%H:%M:%S")
		else:
			dicc["gold"] = "---"
	except Exception, e:
		dicc["gold"] = "---"

	print dicc
	jsonDict = json.dumps(dicc)

	return HttpResponse(jsonDict, 'application/json')
