from django.apps import apps
from scm_cog.models import Pch, Event, Tmpevent
from django.contrib import admin


class PchsAdmin(admin.ModelAdmin):
	list_display = ['sigla', 'pch_name', 'ugs_number']


admin.site.register(Pch, PchsAdmin)
	


class EventAdmin(admin.ModelAdmin):
	list_display = ['pch', 'interruption', 'description','explain', 'data_stop', 'data_start']
	list_filter = ('pch','interruption')
	search_fields = ['pch']

admin.site.register(Event, EventAdmin)

class TmpeventAdmin(admin.ModelAdmin):
	list_display = ['pch','ug','interruption', 'description', 'data_stop', 'data_start', 'user','explain']
	list_filter = ('pch','interruption')
	search_fields = ['pch','data_stop','interruption']

admin.site.register(Tmpevent, TmpeventAdmin)
