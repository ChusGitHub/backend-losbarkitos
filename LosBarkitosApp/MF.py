 # -*- encoding: utf-8 -*-
from django.http import HttpResponse
from .models import Ticket, Control, PuntoVenta, Vendedor
import json, urllib
from datetime import datetime
import time
from datetime import timedelta, date
import MySQLdb
import decimal
from django.db.models import Avg, Sum
from decimal import *
import thread

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

def MFinsertarTicket(request, precio, p): # si p = 1 -> particular, si p = 0 -> grupo
	# regularizo el precio : los dos ultimos numero son decimales
	global lock
	precio = (float(precio) / 100)
	if p == "1" :
		part_bool = True
	else:
		part_bool = False
	
	lock = thread.allocate_lock()
	lock.acquire()

	control = Control.objects.get()
	num_ticket = control.num_ticket

	control.num_ticket = num_ticket + 1
	try:
		numero_a_controlar = Control.objects.get().num_ticket
		if control.num_ticket <= numero_a_controlar:
			control.num_ticket = numero_a_controlar + 1
		control.save()
	except:
		data = {'error' : 1, 'tipo error' : 'No se ha podido grabar el incremento del numero de ticket'}
		lock.release()
		return HttpResponse(json.dumps(data), 'application/json')

	ticket = Ticket(numero 		= num_ticket,
				    precio		= precio,
				    fecha  		= datetime.now() + timedelta(hours = 2),
				    punto_venta = PuntoVenta.objects.get(codigo = 1), # siempre se vendera desde la oficina de MF
				    vendedor 	= Vendedor.objects.get(codigo = 1), # por el mismo motivo
				    part		= part_bool,
				    blanco		= 1)

	try:
		ticket.save()
	except:
		data = {'error' : 1, 'tipo error' : 'Error en la grabacion del ticket'}
		lock.release()
		return HttpResponse(json.dumps(data), 'application/json')

	data = {'error' : 0 ,'numero': num_ticket, 'precio': precio, 'fecha' : datetime.strftime(ticket.fecha, "%H:%M:%S"), 'punto' : ticket.punto_venta.nombre, 'particular' : part_bool}
	lock.release()
	return HttpResponse(json.dumps(data), 'application/json')

def MFinsertarTicketsMasivos(request, precio, cantidad):
	precio = (float(precio) / 100)

	control = Control.objects.get()
	num_ticket = control.num_ticket

	for numT in xrange(num_ticket, num_ticket + int(cantidad)):
		ticket = Ticket(numero 		= numT,
				    	precio		= precio,
				   	 	fecha  		= datetime.now() + timedelta(hours = 2),
				    	punto_venta = PuntoVenta.objects.get(codigo = 1), # siempre se vendera desde la oficina de MF
				    	vendedor 	= Vendedor.objects.get(codigo = 1), # por el mismo motivo
				    	part		= False,
				    	blanco		= 1)

		try:
			ticket.save()
		except:
			data = {'error' : 1, 'tipo error' : 'Error en la grabacion de tickets'}
			return HttpResponse(json.dumps(data), 'application/json')

	control.num_ticket = num_ticket + int(cantidad)
	try:
		control.save()
	except:
		data = {'error' : 1, 'tipo error' : 'Error en la grabacion del numero de ticket'}

	data = {'error' : 0 ,'numero': numT, 'precio': precio, 'fecha' : datetime.strftime(ticket.fecha, "%H:%M:%S"), 'particular' : False, 'cantidad' : int(cantidad)}

	return HttpResponse(json.dumps(data), 'application/json')


def MFmodificarTicket(request, numero, precio):
	precio = (float(precio) / 100)
	try:
		ticket = Ticket.objects.get(numero = numero)
	except Ticket.DoesNotExist:
		data = {'error' : 1, 'tipo error' : 'No se ha podido recuperar el ticket o no existe'}
		return HttpResponse(json.dumps(data), 'application/json')
	ticket.precio = precio
	ticket.save()
	data = {'error' : 0, 'precio' : precio}
	return HttpResponse(json.dumps(data), 'application/json')

def MFrecuperarTicket(request, numero):
	try:
		ticket = Ticket.objects.get(numero = numero)

		data = {'error' : 0, 'numero' : numero, 'precio' : float(ticket.precio), 'fecha' : datetime.strftime(ticket.fecha, "%H:%M:%S"), 'punto_venta' : 1, 'vendedor' : 1, 'particular' : ticket.part, 'blanco' : ticket.blanco}
		return HttpResponse(json.dumps(data), 'application/json')
	except Ticket.DoesNotExist:
		data = {'error' : 1, 'tipo error' : 'No se ha podido recuperar el ticket o este no existe'}

	return HttpResponse(json.dumps(data), 'application/json')

def MFborrarTicket(request, numero):

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT max(id), max(numero) FROM losbarkitosapp_ticket WHERE year(fecha) = year(now())'
	cursor.execute(llamada)
	array = cursor.fetchone()
	id_borrar = array[0]
	numero_max = array[1]
	db.close()
	# Se baja un numero el Control.numero
	control = Control.objects.get()
	control.num_ticket = control.num_ticket - 1
	control.save()

	try: # Se cambia el numero del ultimo ticket al numero del ticket eliminado
		db2 = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
		cursor2 = db2.cursor()
		llamada2 = 'UPDATE losbarkitosapp_ticket SET numero = \'%s\' WHERE numero=\'%s\' and year(fecha)=year(now())' % (numero, numero_max)
		cursor2.execute(llamada2)
		result = cursor2.fetchone()
		db2.close()

		# Se borra el ticket con el numero pedido
		db3 =  MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
		cursor3 = db3.cursor()
		llamada3 = 'DELETE FROM losbarkitosapp_ticket WHERE id=\'%s\' ' % id_borrar
		cursor3.execute(llamada3)
		result = cursor3.fetchone()
		db3.commit()
		db3.close()

		data = {'error' : 0, 'numero' : numero}
	except Ticket.DoesNotExist:
		data = {'error' : 1, 'tipo error' : 'No se ha podido eliminar el ticket o este no existe'}

	# AQUI TENGO QUE MODIFICAR LOS NUMERO DE LOS TICKETS PARA QUE TODO AJUSTE

	return HttpResponse(json.dumps(data), 'application/json')

def MFlistado(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)
	#tickets = Ticket.objects.filter(fecha__range = [inicio, fin]).order_by('fecha')

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT * FROM LosBarkitosApp_ticket where fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)
	tickets = cursor.fetchall()

	dict_tickets = {}
	datos = {}
	numPart = 0
	numGrup = 0
	i = 1
	for ticket in tickets:
		datos = {'numero' : ticket[1], 'precio' : float(ticket[2]), 'fecha' : datetime.strftime(ticket[3], "%d-%m-%Y %H:%M:%S"), 'punto_venta' : 1, 'vendedor' : 1, 'particular' : ticket[6], 'blanco' : ticket[7]}
		dict_tickets[str(i)] = datos
		i += 1
		if ticket[6] == 1: #  este ticket es particular
			numPart += 1
		else:
			numGrup += 1

	dict_tickets['error'] = 0
	dict_tickets['numero_tickets'] = i - 1
	dict_tickets['numero_particulas'] = numPart
	dict_tickets['numero_grupos'] = numGrup

	try:
		jsonDict = json.dumps(dict_tickets)
	except Exception, e:
		dict_tickets['error'] = e.strerror

	return HttpResponse(json.dumps(dict_tickets), 'application/json')

def MFlistadoMensual(request, mes, ano):

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = "SELECT day(LosBarkitosApp_ticket.fecha), count(*), sum(LosBarkitosApp_ticket.precio), sum(LosBarkitosApp_ticket.precio) / 1.21, sum(LosBarkitosApp_ticket.precio) - sum(LosBarkitosApp_ticket.precio) / 1.21 from LosBarkitosApp_ticket where year(fecha)= '20%s' and month(fecha) = '%s' group by day(fecha) order by(day(fecha))" % (ano, mes)
	cursor.execute(llamada)
	dias = cursor.fetchall()

	dict_dias = {}
	datos = {}
	numPart = 0
	numGrup = 0
	i = 0
	for dia in dias:
		i += 1
		datos = {'fecha' : str(dia[0]) + '-' + str(mes) + '-' + str(ano), 'viajes' : dia[1], 'total' : float(dia[2]), 'neto' : float(dia[3]), 'iva' : float(dia[4])}
		dict_dias[str(i)] = datos

	dict_dias['error'] = 0
	dict_dias['numero_dias'] = i

	try:
		jsonDict = json.dumps(dict_dias)
	except Exception, e:
		dict_dias['error'] = "e.strerror"

	return HttpResponse(json.dumps(dict_dias), 'application/json')


def MFeuros(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)
	#total = Ticket.objects.filter(fecha__range = [inicio, fin]).aggregate(Sum('precio'))
	#media = Ticket.objects.filter(fecha__range = [inicio, fin]).aggregate(Avg('precio'))

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT sum(precio) FROM LosBarkitosApp_ticket where fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	total =  float(cursor.fetchone()[0])
	db.close()

	datos = {}
	datos = {'error' : 0, 'total' : total}
	return HttpResponse(json.dumps(datos), 'application/json')

def MFmedia(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)
	#total = Ticket.objects.filter(fecha__range = [inicio, fin]).aggregate(Sum('precio'))
	#media = Ticket.objects.filter(fecha__range = [inicio, fin]).aggregate(Avg('precio'))

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT avg(precio) FROM LosBarkitosApp_ticket where fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	media =  float(cursor.fetchone()[0])
	db.close()

	datos = {}
	datos = {'error' : 0, 'media' : media}
	return HttpResponse(json.dumps(datos), 'application/json')

def MFestadisticas(request, diaI, mesI, anyoI, diaF, mesF, anyoF):
	inicio = datetime(int(anyoI)+2000, int(mesI), int(diaI),0,0,0)
	fin = datetime(int(anyoF)+2000, int(mesF), int(diaF),23,59,59)

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*), avg(precio), sum(precio) FROM LosBarkitosApp_ticket where fecha between \'%s\' and \'%s\'' % (inicio, fin)
	cursor.execute(llamada)

	fila = cursor.fetchone()

	total_tickets = int(fila[0])
	media =  float(fila[1])
	total_euros = float(fila[2])

	db.close()

	datos = {}
	datos = {'error' : 0, 'media' : media, 'total_tickets' : total_tickets, 'euros' : total_euros}
	return HttpResponse(json.dumps(datos), 'application/json')
