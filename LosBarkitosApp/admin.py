# -*- encoding: utf-8 -*-
from django.contrib import admin
from models import *
from datetime import datetime

# Con esta clase configuramos la interfaz de la administracion en Viaje
class ViajeAdmin(admin.ModelAdmin):
	list_display = ('numero', 'barca', 'precio', 'punto_venta', 'fecha', 'vendedor',) # campos que aparecen
	list_filter = ('fecha','punto_venta', 'barca', 'vendedor', ) # filtra por estos campos
	list_editable = ('barca', 'precio',)
	ordering = ('fecha',)

class TicketAdmin(admin.ModelAdmin):
	list_display = ('numero', 'precio', 'punto_venta', 'fecha', 'vendedor',)
	list_filter = ('fecha', 'punto_venta',)
	list_editable = ('precio', 'fecha',)
	ordering = ('fecha',)

class BarcaAdmin(admin.ModelAdmin):
	list_display = ('codigo', 'nombre', 'tipo_barca', 'libre', 'control', 'disponible', )
	ordering = ('libre', 'codigo',)
	list_editable = ('libre','control',)

	# agrego el campo disponible que no pertenece a la BDD
	def disponible(self, obj):
		return obj.control == 0
	disponible.boolean = True

class ReservaAdmin(admin.ModelAdmin):
	list_display = ('numero', 'punto_venta', 'tipo_barca', 'horareserva', 'horaprevista', 'fuera',)

	def horareserva(self, obj):
		return datetime.time(obj.hora_reserva).isoformat()
	def horaprevista(self, obj):
		return datetime.time(obj.hora_prevista).isoformat()

class ControlAdmin(admin.ModelAdmin):
	list_display = ('num_viaje', 'num_ticket', 'num_negro', 'libre', 'num_reserva_rio', 'num_reserva_electrica', 'num_reserva_gold', 'num_reserva_whaly',)
	list_editable = ('num_viaje', 'num_ticket', 'num_negro', 'libre', 'num_reserva_rio', 'num_reserva_electrica', 'num_reserva_gold', 'num_reserva_whaly',)

admin.site.register(Barca, BarcaAdmin)
admin.site.register(TipoBarca)
admin.site.register(Vendedor)
admin.site.register(PuntoVenta)
admin.site.register(Viaje, ViajeAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Control, ControlAdmin)

# Register your models here.
