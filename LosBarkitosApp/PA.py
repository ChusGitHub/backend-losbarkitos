# -*- encoding: utf-8 -*-
from django.http import HttpResponse
from .models import Control, ExcursionPalante, Palante, PuntoVenta
import json, urllib
from datetime import datetime, timedelta, date
import time
import MySQLdb

def PAinsertarTicket(request, exc, AN, PV, blanco):
	excursion = ExcursionPalante.objects.get(codigo = exc)
	puntoventa = PuntoVenta.objects.get(codigo = PV)
	if AN == "A": #adulto
		precio = excursion.adulto
	else:
		precio = excursion.nino
	control = Control.objects.get()
	num_ticket = control.num_ticket_palante
	ticket = Palante(numero 		= num_ticket,
				     precio			= precio,
				     fecha			= datetime.now() + timedelta(hours = 2),
				     punto_venta	= puntoventa,
				     excursion 		= excursion,
				     blanco			= 1)

	try:
		ticket.save()
	except:
		data = {'error' : 1, 'tipo' : 'error en la grabación del viaje en la BDD'}
		return HttpResponse(json.dumps(data), 'application/json')

	data = {'error' : 0, 'numero' : num_ticket, 'excursion' : excursion.excursion, 'precio' : precio, 'fecha' : datetime.strftime(ticket.fecha, "%H:%M:%S"), 'punto' : puntoventa.nombre}

	control.num_ticket_palante = control.num_ticket_palante + 1

	try:
		control.save()
	except:
		data = {'error' : 1, 'tipo' : 'No se ha podido grabar incremento del numero de ticket'}
		return HttpResponse(json.dumps(data), 'application/json')

	return HttpResponse(json.dumps(data), 'application/json')

def PAlistado(request, diaI, mesI, anyoI, diaF, mesF, anyoF, excursion):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT * FROM LosBarkitosApp_palante where excursion_id = \'%s\' and fecha between \'%s\' and \'%s\'' % (excursion, inicio, fin)
	cursor.execute(llamada)
	tickets = cursor.fetchall()
	dict_tickets = {}
	datos = {}
	i = 1
	
	for ticket in tickets:
		PV = PuntoVenta.objects.get(codigo = int(ticket[4]))
		excursion = ExcursionPalante.objects.get(id = int(ticket[5]))
		datos = {'numero' : ticket[1], 'precio' : float(ticket[2]), 'fecha' : datetime.strftime(ticket[3], "%d-%m-%Y %H:%M:%S"), 'punto_venta' : PV.nombre, 'excursion' : excursion.excursion, 'blanco' : ticket[6]}
		dict_tickets[str(i)] = datos
		i += 1

	dict_tickets['error'] = 0
	dict_tickets['numero_tickets'] = i - 1

	try:
		jsonDict = json.dumps(dict_tickets)
	except Exception, e:
		dict_tickets['error'] = e.strerror

	return HttpResponse(json.dumps(dict_tickets), 'application/json')

# Esta llamada devuelve listado de todos los viajes del dia con su excursion correspondiente
def PAlistado2(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)
	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')

	llamada1 = "SELECT id FROM LosBarkitosApp_excursionpalante"
	cursor1 = db.cursor()
	cursor1.execute(llamada1)
	ids = cursor1.fetchall()

	datos = {}
	tickets = {}
	dict_datos = {}
	i = 0
	for exc in ids:
		cursor2 = db.cursor()
		llamada2 = 'SELECT numero, precio, fecha, punto_venta_id FROM LosBarkitosApp_palante where excursion_id = \'%s\' and fecha between \'%s\' and \'%s\'' % (exc[0], inicio, fin)
		cursor2.execute(llamada2)
		tickets = cursor2.fetchall()
		for ticket in tickets:
			datos = {'numero' : ticket[0], 'precio' : float(ticket[1]), 'fecha' : datetime.strftime(ticket[2], "%d-%m-%Y %H:%M:%S"), 'punto_venta' : ticket[3], 'excursion_id' : exc[0]}
			dict_datos[str(i)] = datos
			i += 1
	return HttpResponse(json.dumps(dict_datos), 'application/json')

def PAestadisticas(request, diaI, mesI, anyoI, diaF, mesF, anyoF, excursion):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*), avg(precio), sum(precio) FROM LosBarkitosApp_palante where excursion_id = \'%s\' and fecha between \'%s\' and \'%s\'' % (excursion, inicio, fin)
	cursor.execute(llamada)

	fila = cursor.fetchone()

	total_tickets = int(fila[0])
	media =  float(fila[1])
	total_euros = float(fila[2])

	db.close()

	datos = {}
	datos = {'error' : 0, 'media' : media, 'total_tickets' : total_tickets, 'euros' : total_euros}
	return HttpResponse(json.dumps(datos), 'application/json')

def PAlistadoMensual(request, mes, ano, excursion):

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = "SELECT day(LosBarkitosApp_palante.fecha), count(*), sum(LosBarkitosApp_palante.precio), sum(LosBarkitosApp_palante.precio) / 1.21, sum(LosBarkitosApp_palante.precio) - sum(LosBarkitosApp_palante.precio) / 1.21 from LosBarkitosApp_palante where excursion_id = \'%s\' and  year(fecha)= '20%s' and month(fecha) = '%s' group by day(fecha) order by(day(fecha))" % (excursion, ano, mes)
	cursor.execute(llamada)
	dias = cursor.fetchall()

	dict_dias = {}
	datos = {}
	i = 0

	for dia in dias:
		i += 1
		exc = ExcursionPalante.objects.get(id = excursion)
		datos = {'fecha' : str(dia[0]) + '-' + str(mes) + '-' + str(ano), 'viajes' : dia[1], 'total' : float(dia[2]), 'neto' : float(dia[3]), 'iva' : float(dia[4]), 'excursion' : exc.excursion}
		dict_dias[str(i)] = datos

	dict_dias['error'] = 0
	dict_dias['numero_dias'] = i 

	try:
		jsonDict = json.dumps(dict_dias)
	except Exception, e:
		dict_dias['error'] = "e.strerror"

	return HttpResponse(json.dumps(dict_dias), 'application/json')

def PArecuperarTicket(request, numero):
	try:
		ticket = Palante.objects.get(numero = numero)

		data = {'error' : 0, 'numero' : numero, 'precio' : float(ticket.precio), 'fecha' : datetime.strftime(ticket.fecha, "%H:%M:%S"), 'punto_venta' : ticket.punto_venta.nombre, 'excursion' : ticket.excursion.excursion, 'blanco' : ticket.blanco}
		return HttpResponse(json.dumps(data), 'application/json')
	except Palante.DoesNotExist:
		data = {'error' : 1, 'tipo error' : 'No se ha podido recuperar el ticket o este no existe'}

	return HttpResponse(json.dumps(data), 'application/json')

def PAlistadoMensual(request, mes, ano):

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = "SELECT day(LosBarkitosApp_palante.fecha), count(*), sum(LosBarkitosApp_palante.precio), sum(LosBarkitosApp_palante.precio) / 1.21, sum(LosBarkitosApp_palante.precio) - sum(LosBarkitosApp_palante.precio) / 1.21 from LosBarkitosApp_palante where year(fecha)= '20%s' and month(fecha) = '%s' group by day(fecha) order by(day(fecha))" % (ano, mes)
	cursor.execute(llamada)
	dias = cursor.fetchall()

	dict_dias = {}
	datos = {}

	i = 0
	for dia in dias:
		i += 1
		datos = {'fecha' : str(dia[0]) + '-' + str(mes) + '-' + str(ano), 'tickets' : dia[1], 'total' : float(dia[2]), 'neto' : float(dia[3]), 'iva' : float(dia[4])}
		dict_dias[str(i)] = datos

	dict_dias['error'] = 0
	dict_dias['numero_dias'] = i

	try:
		jsonDict = json.dumps(dict_dias)
	except Exception, e:
		dict_dias['error'] = "e.strerror"

	return HttpResponse(json.dumps(dict_dias), 'application/json')

