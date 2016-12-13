# -*- encoding: utf-8 -*-
from rest_framework import serializers
from .models import Barca

class BarcaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Barca
		fields = ('codigo', 'nombre', 'tipo_barca', 'libre', 'control',)

