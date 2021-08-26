from django.db import models
from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf import settings	


class Pch(models.Model):
	pch_name = models.CharField(max_length=50)
	sigla = models.CharField(max_length=4)
	ugs_number = models.IntegerField()
	created_at = models.DateField(auto_now_add=True)
	class Meta:
		db_table = 'pchs'
	def __str__(self):
		return self.sigla
		#"Retorna a sigla da PCH."
		#return "{} - {}".format(self.sigla, self.descricao)
    

class Event(models.Model):
	data_stop = models.DateTimeField(null=True, blank=True)
	data_start = models.DateTimeField(null=True, blank=True)
	interruption = models.CharField(max_length=75)
	description = models.CharField(max_length=75)
	explain = models.CharField(max_length=150)
	pch = models.ForeignKey(Pch, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ug = models.IntegerField();
	created_at = models.DateField(auto_now_add=True)
	class Meta:
		unique_together = (('data_stop', 'ug', 'pch'),)
		db_table = 'events'

class Tmpevent(models.Model):
	pch = models.ForeignKey(Pch, on_delete=models.CASCADE)
	ug = models.IntegerField();
	data_stop = models.DateTimeField(null=True, blank=True)
	data_start = models.DateTimeField(null=True, blank=True)
	interruption = models.CharField(max_length=75)
	description = models.CharField(max_length=75)
	explain = models.CharField(max_length=150)
	created_at = models.DateField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	class Meta:
		unique_together = (('data_stop', 'ug', 'pch'),)
		db_table = 'tmp_event'
		
	



