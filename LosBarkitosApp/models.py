# -*- coding: utf-8 -*-
from django.db import models
from decimal import *

# Create your models here.
class PuntoVenta(models.Model):
	codigo = models.IntegerField()
	nombre = models.CharField(max_length = 20)

	def __unicode__(self):
		return "%s".encode('utf8') % (self.nombre)

class TipoBarca(models.Model):
	codigo = models.IntegerField()
	tipo   = models.CharField(max_length = 10)

	def __unicode__(self):
		return "%s".encode('utf8') % (self.tipo)

class Barca(models.Model):
	codigo 		= models.IntegerField()
	nombre	    = models.CharField(max_length = 15)
	tipo_barca  = models.ForeignKey(TipoBarca)
	libre		= models.DateTimeField(default = None)
	control     = models.IntegerField(default = 0) # 0 : barca libre
												   # 999: barca no operativa
												   # >1: numero de vueltas por hacer
	navegando	= models.IntegerField(default = 0)
	llegada_base= models.DateTimeField(default = None)

	def __unicode__(self):
		return "%s - %i".encode('utf8') % (self.nombre, self.control)
	class meta:
		ordering=['libre']

class Vendedor(models.Model):
	codigo = models.IntegerField()
	nombre = models.CharField(max_length = 50)

	def __unicode__(self):
		return "%i%s".encode('utf8') % (self.codigo,self.nombre)

class Reserva(models.Model):
	numero 		  = models.IntegerField()
	punto_venta   = models.ForeignKey(PuntoVenta)
	tipo_barca	  = models.ForeignKey(TipoBarca)
	hora_reserva  = models.DateTimeField()
	hora_prevista = models.DateTimeField()
	fuera		  = models.BooleanField(default = False)

	def __unicode__(self):
		return  "%s".encode('utf8') % (self.numero)

class Ticket(models.Model):
	numero		  = models.IntegerField()
	precio		  = models.DecimalField(max_digits = 5, decimal_places = 2)
	fecha		  = models.DateTimeField()
	punto_venta   = models.ForeignKey(PuntoVenta)
	vendedor      = models.ForeignKey(Vendedor)
	part		  = models.BooleanField(default = False)
	blanco		  = models.BooleanField(default = True)

	def __unicode__(self):
		return "Numero: %i".encode('utf8') % (self.numero)

class Viaje(models.Model):
	numero		  = models.IntegerField()
	precio		  = models.IntegerField()
	fecha  	 	  = models.DateTimeField()
	punto_venta	  = models.ForeignKey(PuntoVenta)
	barca 		  = models.ForeignKey(TipoBarca)
	vendedor 	  = models.ForeignKey(Vendedor)
	blanco		  = models.BooleanField(default = True)

	class meta:
		ordering = ['-numero']

	def __unicode__(self):
		return "Numero: %s, fecha: %s".encode('utf8') % (self.numero ,str(self.fecha))

class Control(models.Model):
	num_viaje	  		  = models.IntegerField()
	num_ticket 	  		  = models.IntegerField()
	num_negro	  		  = models.IntegerField()
	libre		  		  = models.DateTimeField(default = None)
	num_reserva_rio		  = models.IntegerField()
	num_reserva_electrica = models.IntegerField()
	num_reserva_gold	  = models.IntegerField()
	num_reserva_whaly	  = models.IntegerField()
	control1			  = models.IntegerField()
	#control2			  = models.IntegerField()


