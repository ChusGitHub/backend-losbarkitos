 # -*- encoding: utf-8 -*-
from django.http import HttpResponse
from .models import Ticket, Control, PuntoVenta, Vendedor, Viaje, TipoBarca
import json, urllib
from datetime import datetime
import time
from datetime import timedelta, date
import MySQLdb
import decimal
from django.db.models import Avg, Sum
from decimal import *

class DecimalEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Decimal):
			return "%.2f" % obj
		return json.JSONEncoder.default(self, obj)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def LBinsertarViaje(request, precio, tipo, blanco):

	precio = (float(precio) / 100)

	control = Control.objects.get()
	num_viaje = control.num_viaje
	barca = TipoBarca.objects.get(codigo = tipo)

	viaje = Viaje(numero 		= num_viaje,
				    precio		= precio,
				    fecha  		= datetime.now() + timedelta(hours = 1),
				    punto_venta = PuntoVenta.objects.get(codigo = 1), # siempre se vendera desde la oficina de MF
				    barca		= TipoBarca.objects.get(codigo = tipo),
				    vendedor 	= Vendedor.objects.get(codigo = 1), # por el mismo motivo
				    blanco		= 1) # De momento desde marinaFerry solo se introducirá tiquets en blanco

	try:
		viaje.save()
	except:
		data = {'error' : 1, 'tipo error' : 'Error en la grabacion del viaje'}
		return HttpResponse(json.dumps(data), 'application/json')

	data = {'error' : 0 ,'numero': num_viaje, 'precio': precio, 'fecha' : datetime.strftime(viaje.fecha, "%d.%m.%y"), 'punto' : viaje.punto_venta.nombre, 'tipo' : int(tipo), 'barca' : barca.tipo}

	control.num_viaje = num_viaje + 1

	try:
		control.save()
	except:
		data = {'error' : 1, 'tipo error' : 'No se ha podido grabar el incremento del numero de ticket'}
		return HttpResponse(json.dumps(data), 'application/json')

	return HttpResponse(json.dumps(data), 'application/json')


def LBlistado(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)
	#tickets = Ticket.objects.filter(fecha__range = [inicio, fin]).order_by('fecha')

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT * FROM LosBarkitosApp_viaje where fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)
	tickets = cursor.fetchall()

	dict_tickets = {}
	datos = {}

	i = 1
	for ticket in tickets:
		datos = {'numero' : ticket[1], 'precio' : float(ticket[2]), 'fecha' : datetime.strftime(ticket[3], "%d-%m-%Y %H:%M:%S"), 'punto_venta' : ticket[4], 'barca' : ticket[5], 'vendedor' : ticket[6], 'blanco' : ticket[7]}
		dict_tickets[str(i)] = datos
		i += 1

	dict_tickets['error'] = 0
	dict_tickets['numero_tickets'] = i - 1

	try:
		jsonDict = json.dumps(dict_tickets)
	except Exception, e:
		dict_tickets['error'] = e.strerror

	return HttpResponse(json.dumps(dict_tickets), 'application/json')

def LBlistadoB(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)
	#tickets = Ticket.objects.filter(fecha__range = [inicio, fin]).order_by('fecha')

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT * FROM LosBarkitosApp_viaje where blanco = true and fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)
	tickets = cursor.fetchall()

	dict_tickets = {}
	datos = {}

	i = 1
	for ticket in tickets:
		datos = {'numero' : ticket[1], 'precio' : float(ticket[2]), 'fecha' : datetime.strftime(ticket[3], "%d-%m-%Y %H:%M:%S"), 'punto_venta' : ticket[4], 'barca' : ticket[5], 'vendedor' : ticket[6], 'blanco' : ticket[7]}
		dict_tickets[str(i)] = datos
		i += 1

	dict_tickets['error'] = 0
	dict_tickets['numero_tickets'] = i - 1

	try:
		jsonDict = json.dumps(dict_tickets)
	except Exception, e:
		dict_tickets['error'] = e.strerror

	return HttpResponse(json.dumps(dict_tickets), 'application/json')

def LBlistadoMensualB(request, mes, ano):

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = "SELECT day(LosBarkitosApp_viaje.fecha), count(*), sum(LosBarkitosApp_viaje.precio), sum(LosBarkitosApp_viaje.precio) / 1.21, sum(LosBarkitosApp_viaje.precio) - sum(LosBarkitosApp_viaje.precio) / 1.21 from LosBarkitosApp_viaje where blanco = true and year(fecha)= '20%s' and month(fecha) = '%s' group by day(fecha) order by(day(fecha))" % (ano, mes)
	print(llamada)
	cursor.execute(llamada)
	dias = cursor.fetchall()

	dict_dias = {}
	datos = {}

	i = 0

	for dia in dias:
		i += 1
		datos = {'fecha' : str(dia[0]) + '-' + str(mes) + '-' + str(ano), 'viajes' : dia[1], 'total' : float(dia[2]), 'neto' : float(dia[3]), 'iva' : float(dia[4])}
		dict_dias[str(i)] = datos

	dict_dias['error'] = 0
	dict_dias['numero_dias'] = i - 1

	try:
		jsonDict = json.dumps(dict_dias)
	except Exception, e:
		dict_dias['error'] = "e.strerror"

	return HttpResponse(json.dumps(dict_dias), 'application/json')

def LBlistadoMensual(request, mes, ano):

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = "SELECT day(LosBarkitosApp_viaje.fecha), count(*), sum(LosBarkitosApp_viaje.precio), sum(LosBarkitosApp_viaje.precio) / 1.21, sum(LosBarkitosApp_viaje.precio) - sum(LosBarkitosApp_viaje.precio) / 1.21 from LosBarkitosApp_viaje where year(fecha)= '20%s' and month(fecha) = '%s' group by day(fecha) order by(day(fecha))" % (ano, mes)
	cursor.execute(llamada)
	dias = cursor.fetchall()

	dict_dias = {}
	datos = {}

	i = 0

	for dia in dias:
		i += 1
		datos = {'fecha' : str(dia[0]) + '-' + str(mes) + '-' + str(ano), 'viajes' : dia[1], 'total' : float(dia[2]), 'neto' : float(dia[3]), 'iva' : float(dia[4])}
		dict_dias[str(i)] = datos

	dict_dias['error'] = 0
	dict_dias['numero_dias'] = i - 1

	try:
		jsonDict = json.dumps(dict_dias)
	except Exception, e:
		dict_dias['error'] = "e.strerror"

	return HttpResponse(json.dumps(dict_dias), 'application/json')


def LBestadisticas(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*), avg(precio), sum(precio) FROM LosBarkitosApp_viaje where punto_venta_id = 1 and fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	fila = cursor.fetchone()

	try:
		total_tickets = int(fila[0])
		media =  float(fila[1])
		total_euros = float(fila[2])

	except:
		datos = {'error' : 1, 'descripcion' : 'No hay viajes para este día' }
		return HttpResponse(json.dumps(datos), 'application/json')		

	db.close()

	datos = {}
	datos = {'error' : 0, 'media' : media, 'total_tickets' : total_tickets, 'euros' : total_euros}
	return HttpResponse(json.dumps(datos), 'application/json')

def LBestadisticasB(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*), avg(precio), sum(precio) FROM LosBarkitosApp_viaje where punto_venta_id = 1  and blanco = true and fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	fila = cursor.fetchone()

	total_tickets = int(fila[0])
	media =  float(fila[1])
	total_euros = float(fila[2])

	db.close()

	datos = {}
	datos = {'error' : 0, 'media' : media, 'total_tickets' : total_tickets, 'euros' : total_euros}
	return HttpResponse(json.dumps(datos), 'application/json')

def LBestadisticasTotalesB(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*), sum(precio) FROM LosBarkitosApp_viaje where  blanco = true and fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	fila = cursor.fetchone()
	print(fila)
	total_tickets = int(fila[0])
	total_euros = float(fila[1])

	db.close()

	datos = {}
	datos = {'error' : 0, 'total_tickets' : total_tickets, 'euros' : total_euros}
	return HttpResponse(json.dumps(datos), 'application/json')

def LBestadisticasTotales(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*), sum(precio) FROM LosBarkitosApp_viaje where  fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	fila = cursor.fetchone()

	total_tickets = int(fila[0])
	total_euros = float(fila[1])

	db.close()

	datos = {}
	datos = {'error' : 0, 'total_tickets' : total_tickets, 'euros' : total_euros}
	return HttpResponse(json.dumps(datos), 'application/json')

def LBhayBarcas(request):
	control = Control.objects.get()
	rio =  int(control.num_reserva_rio)
	elec = int(control.num_reserva_electrica)
	gold = int(control.num_reserva_gold)
	datos = {}

	if  (rio + elec + gold) > 3:
		datos = {'hayBarcas' : 'SI'}	
	else:
		datos = {'hayBarcas' : 'NO'}

	return HttpResponse(json.dumps(datos), 'application/json')

	


