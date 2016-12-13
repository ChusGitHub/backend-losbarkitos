 # -*- encoding: utf-8 -*-
from django.http import HttpResponse
from .models import Barca, Control, Reserva, TipoBarca, Viaje
import json, urllib
from datetime import datetime, time
from datetime import timedelta
import MySQLdb

# Funciones para el control de las barcas
'''
JSON CON LAS BARCAS QUE ESTAN POR LLEGAR POR ORDEN DE LLEGADA
'''
# No se tiene en cuenta la hora en que queda libre la barca, sino la hora en que llega a la base
def llegada(request, tipo):

	# Se recoge la lista de barcas fuera por orden de llegada y segun el tipo de barca
	if tipo == 0:
		listaBarcas = Barca.objects.all().order_by('tipo_barca','libre', 'control', 'codigo',)
	else:
		listaBarcas = Barca.objects.filter(tipo_barca = tipo, libre__isnull = False).order_by('tipo_barca','libre', 'control', 'codigo',)
	print 'listaBarcas: %s' % listaBarcas
	indice = 0
	data = {}
	dict_data = {}

	for barca in listaBarcas:
		indice += 1
		if barca.libre == None: # quiere decir que la barca esta libre
			hora = 'libre'
			hora_llega_base = 'libre'
		else:
			hora = barca.libre.isoformat()
			hora_llega_base = barca.libre - timedelta(hours = barca.control)

		data = {'indice' : indice, 'tipo' : tipo, 'nombre' : barca.nombre, 'libre' : hora, 'vueltas' : barca.control, 'llega' : hora_llega_base.isoformat()}
		dict_data[str(indice)] = data

	# ahora ordeno 'dict_data' los indices para ordenarlos para la llegada
	#print 'dict_data %s ' % dict_data
	aux = 0
	act = {}
	aux = {}
	#print indice
	for i in range(2, indice + 1):
		for j in range(1, indice + 1 - i):
			#print '%i - %i' % (i,j)
			#print dict_data[str(j)]["llega"]
			if dict_data[str(j)]["llega"] > dict_data[str(j+1)]["llega"]: # intercambio indices
				aux = dict_data[str(j)]["indice"]
				dict_data[str(j)]["indice"] = dict_data[str(j+1)]["indice"]
				dict_data[str(j+1)]["indice"] = aux

	#print 'dict_data ordenado : %s ' % dict_data
	return HttpResponse(json.dumps(dict_data), 'application/json')

'''
JSON CON LAS BARCAS QUE ESTAN FUERA POR ORDEN DE LLEGADA
'''
def barcasFuera(request):
	#lista_fuera = Barca.objects.all().order_by('libre')

	#data = {}
	#lista_data = []
	#for barca in lista_fuera:
	#		if barca.libre != None:
	#		tipo = barca.tipo_barca
	#		hora = datetime.time(barca.libre).isoformat()
	#		data = {'Nombre' : barca.nombre, 'Tipo' : tipo.tipo, 'libre' : hora}
	#		lista_data.append(data)
	TBRio = TipoBarca.objects.get(codigo = 1)
	TBElectrica = TipoBarca.objects.get(codigo = 2)
	TBWhaly = TipoBarca.objects.get(codigo = 3)
	TBGold = TipoBarca.objects.get(codigo = 4)
	fuera = [0,0,0,0]
	fuera[0] = Barca.objects.filter(tipo_barca = TBRio, navegando = 1).count()
	fuera[1] = Barca.objects.filter(tipo_barca = TBElectrica, navegando = 1).count()
	fuera[2] = Barca.objects.filter(tipo_barca = TBWhaly, navegando = 1).count()
	fuera[3] = Barca.objects.filter(tipo_barca = TBGold, navegando = 1).count()
	data = {}
	data = {'fuera' : fuera}
	return HttpResponse(json.dumps(data), "application/json")

'''
DEVUELVE UN JSON CON LA PRIMERA BARCA DISPONIBLE SEGUN TIPO BARCA
'''
def primeraLibre(request):
	lista = {}
	primera_rio = Barca.objects.filter(tipo_barca = 1).order_by('control', 'libre', 'codigo')[0]
	print 'primera rio:---'
	print primera_rio
	primera_barca = Barca.objects.filter(tipo_barca = 2).order_by('control', 'libre', 'codigo')[0]
	print 'primera barca:---'
	print primera_barca.nombre
	primera_gold = Barca.objects.filter(tipo_barca = 3).order_by('control', 'libre', 'codigo')[0]
	#primera_gold = Barca.objects.filter(tipo_barca = 4).order_by('control', 'libre')[0]
	print 'primera barca:---'
	print primera_barca.nombre
	try:
		rio = {'nombre' : primera_rio.nombre, 'libre' : datetime.time(primera_rio.libre).isoformat(), 'control' : primera_rio.control}
	except TypeError:
		rio = {'nombre' : primera_rio.nombre, 'libre' : 'libre', 'control' : primera_rio.control}

	try:
		barca = {'nombre' : primera_barca.nombre, 'libre' : datetime.time(primera_barca.libre).isoformat(), 'control' : primera_barca.control}
	except TypeError:
		barca = {'nombre' : primera_barca.nombre, 'libre' : 'libre', 'control' : primera_barca.control}

	try:
		gold = {'nombre' : primera_gold.nombre, 'libre' : datetime.time(primera_gold.libre).isoformat(), 'control' : primera_gold.control}
	except TypeError:
		gold = {'nombre' : primera_gold.nombre, 'libre' : 'libre', 'control' : primera_gold.control}

	lista["rio"] 	   = rio
	lista["barca"]	   = barca
	lista["gold"] 	   = gold

	return HttpResponse(json.dumps(lista), 'application/json')

# Hace el control de la salida de una barca
def salidaBarca(request, tipo): # tipo 1|2|3|4 segun el tipo de barc
	#	RECOGE EL TIPO DE BARCA Y ACTUALIZA LA BDD CON LA SALIDA DE ESA BARCA
		# recupero la barca solicitada para salida

	try:
		barca = Barca.objects.filter(tipo_barca = tipo, control__lt = 999, navegando = 0).order_by('libre', '-control')[0]
		print 'Barca Escogida - ';print barca.nombre;print "--"
	except:
		return HttpResponse(json.dumps({'error': 'no es posible'}), 'application/json')

	# si "libre" = None -> barca parada
	# si "libre" != None y control == 0 -> barca circulando pero no tiene reservas

	if barca.control == 0 and barca.libre == None:
		print 'entra 11111111111'
		barca.libre = (datetime.now() + timedelta(hours=3)).isoformat() #UTC +2 + 1 hora de navegacion
	elif barca.control == 0 and barca.libre != None: # esta opcion no se puede dar
		print 'entra 222222222222'
		#return HttpResponse(json.dumps({'error': 'no es posible'}), 'application/json')
	elif barca.control > 0:
		print 'entra 333333333333333'
		if barca.control != 999:
			barca.control -= 1
	barca.navegando = 1
	barca.llegada_base = (datetime.now() + timedelta(hours=3)).isoformat()
	try:
		barca.save()
		data = {'nombre' : barca.nombre, 'libre' : datetime.time(barca.libre).isoformat(), 'tipo' : tipo}
	except TypeError: # puede decir que barca.libre = None y fallaria
		barca.save()
		data = {'nombre' : barca.nombre, 'libre' : 'None', 'tipo' : tipo}

	return HttpResponse(json.dumps(data), 'application/json')


# ESTE METODO RECOGE UNA LLEGADA DE UNA BARCA SEGUN SU TIPO Y DEVUELVE EL CODIGO DE LA BARCA QUE LLEGA
# tipo en este metodo es un string con el nombre del tipo
def llegadaBarca(request, tipo):
	#if hayReservas:
	# RECOGE EL TIPO DE BARCA Y ACTUALIZA LA BDD CON LA LLEGADA DE LA BARCA
	url = "http://losbarkitos.herokuapp.com/orden_llegada/%s/" % tipo
	respuesta = urllib.urlopen(url)

	json_data = {}
	json_data = json.loads(respuesta.read())
	print len(json_data)
	if len(json_data) < 1:
		data = {'error': "1"}
		return HttpResponse(json.dumps(data), 'application/json')
	#print 'barca que llega : %s' % barca["nombre"]
	barca = json_data["1"]
	barcaModel = Barca.objects.get(nombre = barca["nombre"])
	barcaModel.navegando = 0
	barcaModel.llegada_base = None
	if barcaModel.libre != None and barcaModel.control == 0:
		#print ' entra en if'
		barcaModel.libre = None

	barcaModel.save()

	data = {} 
	try:
		data = {'nombre' : barcaModel.nombre, 'error' : "0", 'tipo' : tipo}
	except Exception, e:
		data = {'error': "1", 'tipo' : tipo}

	return HttpResponse(json.dumps(data), 'application/json')


def noDisponible(request, num_barca):
	barca = Barca.objects.get(codigo = num_barca)
	barca.control = 2 # barca averiada
	barca.libre = None

	try:
		barca.save()
		data = {'exito':barca.codigo, 'error':0}
	except Exception, e:
		data = {'exito':0, 'error': 'Error numero %s de %s' % (e.errno, e.strerror)}

	return HttpResponse(json.dumps(data), 'application/json')

def disponible(request, num_barca):
	barca = Barca.objects.get(codigo = num_barca)
	barca.control = 0 # barca averiada
	barca.libre = None

	try:
		barca.save()
		data = {'exito':barca.codigo, 'error':0}
	except Exception, e:
		data = {'exito':0, 'error': 'Error numero %s de %s' % (e.errno, e.strerror)}

	return HttpResponse(json.dumps(data), 'application/json')

# Resetea tanto la tabla Barca como la tabla de Reservas y los campos de control adecuados
def resetear(request):
	barcas = Barca.objects.all()
	control = Control.objects.all()[0]
	reservas = Reserva.objects.all()

	try:
		for barca in barcas:
			barca.control = 0
			barca.libre = None
			barca.save()
		#for control in controls
		control.num_viaje = 0
		control.num_reserva = 0
		control.libre = None
		control.reserva_rio = 0
		control.reserva_electrica = 0
		control.reserva_whaly = 0
		control.reserva_gold = 0
		control.control1 = 0
		control.save()

		reservas.delete()

		data = {'exito' : 'ok', 'error' : 0}
	except Exception, e:
		data = {'exito':0, 'error': 'Error numero %s de %s' % (e.errno, e.strerror)}


	return HttpResponse(json.dumps(data), 'application/json')

def totalBarcas(request, base):

	dia = datetime.now().strftime("%d");print dia
	mes = datetime.now().strftime("%m");print mes
	ano = datetime.now().strftime("%Y"); print ano

	db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
	cursor = db.cursor()
	llamada = 'SELECT count(*) FROM LosBarkitosApp_viaje where barca_id=1 and punto_venta_id = %s and year(fecha)=%s  and month(fecha)=%s and day(fecha)=%s' % (base, ano, mes, dia)
	cursor.execute(llamada)
	RIOS =  cursor.fetchone()
	llamada = 'SELECT count(*) FROM LosBarkitosApp_viaje where barca_id=2 and punto_venta_id = %s and year(fecha)=%s  and month(fecha)=%s and day(fecha)=%s' % (base, ano, mes, dia)
	cursor.execute(llamada)
	ELECTRICAS = cursor.fetchone()
	llamada = 'SELECT count(*) FROM LosBarkitosApp_viaje where barca_id=3 and punto_venta_id = %s and year(fecha)=%s  and month(fecha)=%s and day(fecha)=%s' % (base, ano, mes, dia)
	cursor.execute(llamada)
	WHALYS = cursor.fetchone()
	llamada = 'SELECT count(*) FROM LosBarkitosApp_viaje where barca_id=4 and punto_venta_id = %s and year(fecha)=%s  and month(fecha)=%s and day(fecha)=%s' % (base, ano, mes, dia)
	cursor.execute(llamada)
	GOLDS = cursor.fetchone()
	db.close()

	try:
		rios = RIOS[0]
	except :
		rios = 0
	try:
		electricas = ELECTRICAS[0]
	except :
		electricas = 0
	try:
		whalys = WHALYS[0]
	except :
		whalys = 0
	try:
		golds = GOLDS[0]
	except :
		golds = 0

	'''try:
		barcas = BARCAS
	except :
		barcas = 0'''


	data = {'rio' : rios, 'electrica' : electricas, 'whaly' : whalys, 'gold' : golds}
	#data = {'barcas' : barcas}
	return HttpResponse(json.dumps(data), 'application/json')

def totalEuros(request, base):

	dia = datetime.now().strftime("%d")
	mes = datetime.now().strftime("%m")
	ano = datetime.now().strftime("%Y")

	try:
		db = MySQLdb.connect(user = 'b17e70697e2374', db='heroku_c71c74c67cde020', passwd='3eaf2e91', host='eu-cdbr-west-01.cleardb.com')
		cursor = db.cursor()
		llamada = 'SELECT sum(precio) FROM LosBarkitosApp_viaje where  punto_venta_id = %s and year(fecha)=%s  and month(fecha)=%s and day(fecha)=%s' % (base, ano, mes, dia)
		cursor.execute(llamada)
		TOTAL =  int(cursor.fetchone()[0])

		db.close()

		if TOTAL is None:
			data = {'total' : 0}
		else:
			data = {'total' : TOTAL}

	except Exception, e:
		data = {'error': e}

	return HttpResponse(json.dumps(data), 'application/json')

