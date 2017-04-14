###VAMOOS
from django.conf.urls import patterns, include, url
from django.contrib import admin

from LosBarkitosApp.views import *
from LosBarkitosApp.controlViaje import *
from LosBarkitosApp.controlVendedor import ventaVendedor, vendedores
from LosBarkitosApp.controlReserva import incrementarReserva, reserva, reserva_fuera, listadoReservas, posibleReserva, cierreDia, barcasDia, totalReservas
from LosBarkitosApp.MF import MFinsertarTicket, MFinsertarTicketsMasivos, MFmodificarTicket, MFrecuperarTicket, MFborrarTicket, MFlistado, MFlistadoMensual, MFeuros, MFmedia, MFestadisticas
from LosBarkitosApp.LB import LBlistado, LBlistadoB, LBestadisticas, LBestadisticasB, LBestadisticasTotales, LBestadisticasTotalesB, LBinsertarViaje, LBlistadoMensual, LBlistadoMensualB, LBhayBarcas

#from LosBarkitosApp.PA import PAinsertarTicket, PAlistado, PAestadisticas, PAlistadoMensual, PAlistado2, PArecuperarTicket, PAlistadoMensual


admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'LosBarkitosProyecto.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^llegada/', include(router.urls)),
    url(r'^orden_llegada/(0|1|2|3|4)/$', llegada),
    url(r'^fuera/', barcasFuera),
    url(r'^primera_libre/', primeraLibre),
    url(r'^salida/(1|2|3|4)/$', salidaBarca),
    url(r'^llegada/(0|1|2|3|4)/$', llegadaBarca),
    url(r'^disponible/([1-9]|1[0-9]|20)/$', disponible),
    url(r'^no_disponible/([1-9]|1[0-9]|20)/$', noDisponible),
    url(r'^api-auth/', include('rest_framework.urls', namespace  = 'rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^barcas/$', 'LosBarkitosApp.views.barcas'),
    url(r'^registro_barca/(\d{1,})/([1-5])/([1-9][0-9]*)/([12345])/([12345])/([01])/$', registroBarca),
    url(r'^venta_vendedor/([1-9])/$', ventaVendedor),
    url(r'^vendedores/$', vendedores),
    url(r'^resetear_barcas/$', resetear),
    url(r'^reserva/(1|2|3|4)/([123])$', reserva),
    url(r'^reserva_fuera/([0-9]+)/$', reserva_fuera),
    #url(r'^listado_viaje/(?P<tipo>[01234])/(?P<pv>[0123])/$', listadoViajes),
    #url(r'^listado_viaje_vendedor/(?P<tipo>[01234])/(?P<pv>[0123])/(?P<vend>[01234])/$', listadoViajesVendedor),

    url(r'^reserva/(1|2|3|4)/([1235])$', reserva),
    url(r'^reserva_fuera/(1|2|3|4)/([0-9]+)/$', reserva_fuera),
    url(r'^listado_viaje/(?P<tipo>[01234])/(?P<pv>[01235])/$', listadoViajes),
    url(r'^ultimo_numero/(\d{1,})/$', ultimoNumero),
    url(r'^ajustar_numero_fallo_impresion/([123])/$', ajustarNumeroFalloImpresion),
    url(r'^total_euros/(1|2|3|4|5|6)$', totalEuros),
    url(r'^total_barcas/(1|2|3|4|5|6)$', totalBarcas),
    # url(r'^numero_barcas/(total|1|2|3|4)$', numeroBarcas),
    url(r'^listado_reservas/(Rio|Barca|Gold)/$', listadoReservas),
    url(r'^posible_reserva/$', posibleReserva),
    url(r'^primera_en_llegar/$', primeraLlegar),
    url(r'^cierre_dia/$', cierreDia),
    url(r'^barcas_dia/$', barcasDia),
    url(r'^total_reservas/$', totalReservas),
    url(r'^LBlistado/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', LBlistado),
    url(r'^LBlistadoB/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', LBlistadoB),
    url(r'^LBlistado_mensual/(\d{1,2})/(\d{1,2})/$', LBlistadoMensual),
    url(r'^LBlistado_mensualB/(\d{1,2})/(\d{1,2})/$', LBlistadoMensualB),
    url(r'^LBestadisticas/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', LBestadisticas),
    url(r'^LBestadisticasB/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', LBestadisticasB),
    url(r'^LBestadisticasTotales/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', LBestadisticasTotales),
    url(r'^LBestadisticasTotalesB/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', LBestadisticasTotalesB),
    url(r'^LBinsertar_viaje/(\d{1,})/([0123456])/([01])/$', LBinsertarViaje),
    url(r'^LBhayBarcas/$', LBhayBarcas),

    #----------------------------------------------------------------------
    # URL para MarinaFerry
    url(r'^MFinsertar_ticket/(\d{1,})/([01])/$', MFinsertarTicket),
    url(r'^MFinsertar_tickets_masivos/(\d{1,})/(\d{1,})/$', MFinsertarTicketsMasivos),
    url(r'^MFmodificar_ticket/(\d{1,})/(\d{1,})/$', MFmodificarTicket),
    url(r'^MFrecuperar_ticket/(\d{1,})/$', MFrecuperarTicket),
    url(r'^MFborrar_ticket/(\d{1,})/$', MFborrarTicket),
    url(r'^MFlistado/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', MFlistado),
    url(r'^MFlistado_mensual/(\d{1,2})/(\d{1,2})/$', MFlistadoMensual),
    url(r'^MFeuros/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', MFeuros),
    url(r'^MFmedia/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', MFmedia),
    url(r'^MFestadisticas/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', MFestadisticas),
    url(r'^incrementar_reserva/(1|2|3)/$', incrementarReserva),
    #--------------------------------------------------------------------------
    # URL para Palante
    #url(r'^PAinsertar_ticket/([1234])/([AN])/([123456789])/([01])/$', PAinsertarTicket),
    #url(r'^PAlistado/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,})/$', PAlistado),
    #url(r'^PAestadisticas/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,})/$', PAestadisticas),
    #url(r'^PAlistado_mensual/(\d{1,2})/(\d{1,2})/(\d{1,})/$', PAlistadoMensual),
    #url(r'^PAlistado2/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/(\d{1,2})/$', PAlistado2),
    #url(r'^PArecuperar_ticket/(\d{1,})/$', PArecuperarTicket),
    #url(r'^PAlistado_mensual/(\d{1,2})/(\d{1,2})/$', PAlistadoMensual),
)
