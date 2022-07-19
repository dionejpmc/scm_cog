from ast import Try
from pydoc import isdata
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
#from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
# -*- encoding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from scm_cog.models import *
from colorama import Fore, Back, Style
import datetime
from django.utils import dateformat, formats, timezone
from django.shortcuts import redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import numpy as np
from django.db import transaction
from django.core.exceptions import *
from django.db import IntegrityError
from django.template.defaulttags import register
import random
#from __future__ import unicode_literals

def HomePageView(request):
    template_name = "home.html"
    return render(request,template_name,{})

def Handler_not_found(request, exception):
    return render(request, 'not-found.html')

@login_required
def MenuPageView(request):
    template_name = "menu/menu_inicio.html"
    return render(request,template_name,{})

@login_required
def ChangePasswordView(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, ('Sua senha foi atualizada!'))
            return redirect('/menu')
        else:
            messages.error(request, ('Houve um erro, tente novamente.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'personal/changepassword.html', {
        'form': form
    })

@login_required
def AddEventsPage(request):
    template_name = "reports/addevents.html"
    all_data = Tmpevent.objects.filter(user_id=request.user.id)
    dif_user = False

    for data in all_data:
        dif = data.data_start - data.data_stop
        data.difference = dif
        data.data_stop = data.data_stop.strftime("%Y-%m-%d %H:%M")
        data.data_start = data.data_start.strftime("%Y-%m-%d %H:%M")
        if data.user.username !=  request.user.username:
            dif_user = True;
    tmp_event = {'all_data': all_data}
    if (dif_user):
        messages.info(request, "Podem haver dados na tabela de indisponibilidade do turno que seu usuário não tem acesso!")
        messages.warning(request, "Converse com o operador do turno anterior, talvez ele não tenha encerrado o turno!")
    return render(request,template_name,tmp_event)

@login_required
def SaveEvents(request):
    if request.method == 'GET':
        tmp_data = Tmpevent()
        if Validate(request):
            try:
                data_start = request.GET['data_start']
                data_stop = request.GET['data_stop']
                format = "%Y-%m-%d %H:%M"
                data_start = data_start.strip('AM')
                data_stop = data_stop.strip('AM')
                data_start = data_start.strip('PM')
                data_stop = data_stop.strip('PM')
                data_start = data_start.replace("/", "-")
                data_stop = data_stop.replace("/", "-")
                data_start = datetime.datetime.strptime(data_start, format)
                data_stop = datetime.datetime.strptime(data_stop, format)
                dif = data_start - data_stop
                tmp_data.data_start = data_start
                tmp_data.data_stop = data_stop
                ug = request.GET['ug']
                ug = ug.replace('UG0', "")
                ug = ug.replace('ug0', "")
                tmp_data.ug = ug
                tmp_data.description = request.GET['justfi']
                tmp_data.interruption = request.GET['cause']
                tmp_data.explain = request.GET['complement']
                tmp_data.user = request.user
                Pch_data = Pch.objects.filter(sigla=request.GET['pch_name'])
                for data_pch in Pch_data:
                    print(Fore.RED)
                    print("Dados do objeto PCH: " + data_pch.pch_name + " sigla: " + data_pch.sigla + " id: " + str(data_pch.id ))
                    print(Style.RESET_ALL)
                tmp_data.pch = data_pch
                with transaction.atomic():
                    tmp_data.save()
                    messages.success(request, 'Dados salvos com sucesso!')
                    all_data = Tmpevent.objects.all()
                    data_tmp_event = {'all_data':all_data}
                del(tmp_data)
                return redirect('.')
            except (IntegrityError, Exception) as e:
                #raise e
                transaction.rollback()
                print(e)
                messages.warning(request, e)
                #logger.error(e)
                del(tmp_data)
                return redirect('.')
        else:
            print("Requisição não permitida!")
            del(tmp_data)
            messages.warning(request, 'Requisição não permitida!')
            return redirect('.')

def Validate(request):
    if (request.GET['justfi'] == "Falha na LT 34,5 Kv" or  request.GET['justfi'] == "Falha na LT 138 Kv" or  request.GET['justfi'] == "Falha na LT 13 Kv" or  request.GET['justfi'] == "Falha na SE" or  request.GET['justfi'] == "Falha na SE Usina" or  request.GET['justfi'] == "Rejeição de Carga para Limpeza de Grade" or  request.GET['justfi'] == "Manutenção na LT 34,5 Kv" or  request.GET['justfi'] == "Manutenção na LT 138 Kv" or  request.GET['justfi'] == "Manutenção na LT 13 Kv" or  request.GET['justfi'] == "Manutenção na SE" or  request.GET['justfi'] == "Manutenção na Unidade" or  request.GET['justfi'] == "Erro no supervisório" or  request.GET['justfi'] == "Trip por temperatura ou pressão") or  request.GET['justfi'] == "DPG (Controle de nível)":
        value = True
        if (request.GET['pch_name'] == "RF" or request.GET['pch_name'] == "SR" or request.GET['pch_name'] == "SM" or request.GET['pch_name'] == "NF") and value:
            value = True
            if (request.GET['cause'] == "IF" or request.GET['cause'] == "MT" or request.GET['cause'] == "IP" or request.GET['cause'] == "DPG") and value:
                value = True
                data_start = request.GET['data_start']
                data_stop = request.GET['data_stop']
                if (data_stop < data_start) and value:
                    value = True
                else:
                    value = False
                    print("Erro de data")
                    messages.error(request, 'Inconsistencia de data.')
            else:
                value = False
                print("Causa Incorreta!")
                messages.error(request, 'Inconsistencia na Causa.')
        else:
            value = False
            print("Nome da PCH incorreto!")
            messages.error(request, 'Inconsistencia no nome da PCH.')
    else:
        value = False
        print("Justificativa incorreta!")
        messages.error(request, 'Inconsistencia na Justificativa.')
    return value
@login_required
def FinaliseWorkShift(request):
    batch_size = 100
    template_name = "reports/addevents.html"
    try:
        with transaction.atomic():
            if (Tmpevent.objects.all().exists()):
                current_user = request.user
                tmp_data = Tmpevent.objects.filter(user_id=current_user.id)
                Event.objects.bulk_create(tmp_data, batch_size)
                Tmpevent.objects.filter(user_id=current_user.id).delete()
            else:
                messages.success(request, 'Seu turno foi finalizado sem dados na tabela de indisponibilidades!')
            messages.success(request, 'Sessão finalizada, você acabou de encerrar seu turno, tenha um bom descanso!')
            request.session.flush()
    except Exception as e:
        messages.warning(request, 'Houve um erro ao finalizar o turno!')
        print("Não salvo")
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        return redirect('.')
    return redirect('.')
    
@login_required
def RemoveLine(request):
    ug = request.GET['ug']
    ug = ug.replace('UG0', "")
    ug = ug.replace('ug0', "")
    pch =  Pch.objects.filter(sigla=request.GET['pch'])
    format = '%Y-%m-%d %H:%M'
    dt_object = request.GET['datastop']
    dt_object = dt_object.lstrip()
    dt_object = datetime.datetime.strptime(dt_object, format)
    datastop = dt_object
    if (Pch.objects.filter(sigla=request.GET['pch']).exists()):
        for x in pch:
            pch_id = x.id
    try:
        object_tmp = Tmpevent.objects.filter(ug=ug).filter(pch=pch_id).filter(data_stop=datastop)
        object_tmp.delete()
        messages.success(request, 'Registro removido!')
    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        messages.warning(e, 'Houve um erro ao remover essa linha')
    return redirect('.')

def Visitor(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip=request.META.get('REMOTE_ADDR')
    return ip

@login_required
def GraphReport(request):
    #data_start = request.GET['data_start']
    #data_stop = request.GET['data_stop']
    somadata01_if = 0;
    somadata01_ip = 0;
    somadata01_dpg = 0;
    somadata01_mt = 0;

    somadata02_if = 0;
    somadata02_ip = 0;
    somadata02_dpg = 0;
    somadata02_mt = 0;

    somadata03_if = 0;
    somadata03_ip = 0;
    somadata03_dpg = 0;
    somadata03_mt = 0;

    somadata04_if = 0;
    somadata04_ip = 0;
    somadata04_dpg = 0;
    somadata04_mt = 0;

    somadata05_if = 0;
    somadata05_ip = 0;
    somadata05_dpg = 0;
    somadata05_mt = 0;

    somadata06_if = 0;
    somadata06_ip = 0;
    somadata06_dpg = 0;
    somadata06_mt = 0;

    somadata07_if = 0;
    somadata07_ip = 0;
    somadata07_dpg = 0;
    somadata07_mt = 0;

    somadata08_if = 0;
    somadata08_ip = 0;
    somadata08_dpg = 0;
    somadata08_mt = 0;

    somadata09_if = 0;
    somadata09_ip = 0;
    somadata09_dpg = 0;
    somadata09_mt = 0;

    somadata10_if = 0;
    somadata10_ip = 0;
    somadata10_dpg = 0;
    somadata10_mt = 0;

    somadata11_if = 0;
    somadata11_ip = 0;
    somadata11_dpg = 0;
    somadata11_mt = 0;

    somadata12_if = 0;
    somadata12_ip = 0;
    somadata12_dpg = 0;
    somadata12_mt = 0;

    kpi_if01 = 0;
    kpi_ip01 = 0;
    kpi_mt01 = 0;
    kpi_dpg01 = 0;
    kpi_if02 = 0;
    kpi_ip02 = 0;
    kpi_mt02 = 0;
    kpi_dpg02 = 0;
    try:
            #https://stackoverflow.com/questions/5895588/django-multivaluedictkeyerror-error-how-do-i-deal-with-it
            if Pch.objects.filter(sigla=request.GET['sigla']).exists():
                pch =  Pch.objects.filter(sigla=request.GET['sigla'])
                pch_id = pch[0].id
                pch_name = pch[0].pch_name
                pch_sigla = pch[0].sigla
            else:
                pch = Pch.objects.all()[:random.choice([1, 2, 3, 4])]
                pch_id = pch[0].id
                pch_name = pch[0].sigla
                pch_sigla = pch[0].sigla
                messages.warning(request,"Pesquisa com valores incorretos! Um valor correto foi automaticamente selecionado pelo sistema.")
    except:
        pch = Pch.objects.first()
        pch_id = pch.id
        pch_name = pch.pch_name
        pch_sigla = pch.sigla
        messages.warning(request,"Pesquisa randomica")
    if request.method == 'GET':
        if ('data_inicial' in request.GET):
            format = "%Y-%m-%d"
            datestop = request.GET['data_inicial']
            try:
                datestop = datetime.datetime.strptime(datestop, format)
            except:
                datestop = datetime.datetime.strptime(str(datetime.date.today()), format)
            data = Event.objects.filter(data_stop__year=datestop.year, pch_id=pch_id).values('data_start','data_stop','ug','pch_id','interruption')
        else:
            data = Event.objects.filter(data_stop__year=datetime.date.today().year, pch_id=pch_id).values('data_start','data_stop','ug','pch_id','interruption')
        for value in data:
            data_month = value['data_stop']
            data_month = data_month.month
            if data_month == 1:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata01_if
                    else:
                        kpi_if02 +=somadata01_if
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata01_ip
                    else:
                        kpi_ip02 +=somadata01_ip
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata01_mtsomadata02_if
                        kpi_mt02 +=somadata01_mt
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata01_dpg
                    else:
                        kpi_dpg02 +=somadata01_dpg
            elif data_month == 2:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata02_if 
                    else:
                        kpi_if02 +=somadata02_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata02_ip 
                    else:
                        kpi_ip02 +=somadata02_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata02_mt 
                    else:
                        kpi_mt02 +=somadata02_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata02_dpg
                    else:
                        kpi_dpg02 +=somadata02_dpg
            elif data_month == 3:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata03_if 
                    else:
                        kpi_if02 +=somadata03_if                    
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata03_ip 
                    else:
                        kpi_ip02 +=somadata03_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata03_mt 
                    else:
                        kpi_mt02 +=somadata03_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata03_dpg
                    else:
                        kpi_dpg02 +=somadata03_dpg
            elif data_month == 4:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata04_if 
                    else:
                        kpi_if02 +=somadata04_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata04_ip 
                    else:
                        kpi_ip02 +=somadata04_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata04_mt 
                    else:
                        kpi_mt02 +=somadata04_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata04_dpg
                    else:
                        kpi_dpg02 +=somadata04_dpg
            elif data_month == 5:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata05_if 
                    else:
                        kpi_if02 +=somadata05_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata05_ip 
                    else:
                        kpi_ip02 +=somadata05_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata05_mt 
                    else:
                        kpi_mt02 +=somadata05_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata05_dpg
                    else:
                        kpi_dpg02 +=somadata05_dpg
            elif data_month == 6:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata06_if 
                    else:
                        kpi_if02 +=somadata06_if 
                    
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata06_ip 
                    else:
                        kpi_ip02 +=somadata06_ip 
                    kpi_ip += somadata06_ip
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata06_mt 
                    else:
                        kpi_mt02 +=somadata06_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata06_dpg
                    else:
                        kpi_if02 +=somadata06_dpg
            elif data_month == 7:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata07_if 
                    else:
                        kpi_if02 +=somadata07_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata07_ip 
                    else:
                        kpi_ip02 +=somadata07_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata07_mt 
                    else:
                        kpi_mt02 +=somadata07_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata07_dpg
                    else:
                        kpi_dpg02 +=somadata07_dpg
            elif data_month == 8:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata08_if 
                    else:
                        kpi_if02 +=somadata08_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata08_ip 
                    else:
                        kpi_ip02 +=somadata08_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata08_mt 
                    else:
                        kpi_mt02 +=somadata08_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata08_dpg 
                    else:
                        kpi_dpg02 +=somadata08_dpg
            elif data_month == 9:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata09_if 
                    else:
                        kpi_if02 +=somadata09_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata09_ip 
                    else:
                        kpi_ip02 +=somadata09_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata09_mt 
                    else:
                        kpi_mt02 +=somadata09_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata09_dpg 
                    else:
                        kpi_dpg02 +=somadata09_dpg
            elif data_month == 10:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata10_if 
                    else:
                        kpi_if02 +=somadata10_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata10_ip 
                    else:
                        kpi_ip02 +=somadata10_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata10_mt 
                    else:
                        kpi_mt02 +=somadata10_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata10_dpg
                    else:
                        kpi_dpg02 +=somadata10_dpg
            elif data_month == 11:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata11_if 
                    else:
                        kpi_if02 +=somadata11_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata11_ip 
                    else:
                        kpi_ip02 +=somadata11_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata11_mt 
                    else:
                        kpi_mt02 +=somadata11_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata11_dpg
                    else:
                        kpi_dpg02 +=somadata11_dpg
            elif data_month == 12:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata12_if 
                    else:
                        kpi_if02 +=somadata12_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata12_ip 
                    else:
                        kpi_ip02 +=somadata12_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata12_mt 
                    else:
                        kpi_mt02 +=somadata12_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata12_dpg
                    else:
                        kpi_dpg02 +=somadata12_dpg
        objeto   = {
                    'pch_name':pch_name,
                    'pch_sigla':pch_sigla,
                    'kpi_if01':kpi_if01,
                    'kpi_ip01':kpi_ip01,
                    'kpi_mt01':kpi_mt01,
                    'kpi_dpg01':kpi_dpg01,
                    'kpi_if02':kpi_if02,
                    'kpi_ip02':kpi_ip02,
                    'kpi_mt02':kpi_mt02,
                    'kpi_dpg02':kpi_dpg02,
                    'somadata01_if':somadata01_if,
                    'somadata01_ip':somadata01_ip,
                    'somadata01_dpg':somadata01_dpg,
                    'somadata01_mt':somadata01_mt,
        
                    'somadata02_if':somadata02_if,
                    'somadata02_ip':somadata02_ip,
                    'somadata02_dpg':somadata02_dpg,
                    'somadata02_mt':somadata02_mt,
        
                    'somadata03_if':somadata03_if,
                    'somadata03_ip':somadata03_ip,
                    'somadata03_dpg':somadata03_dpg,
                    'somadata03_mt':somadata03_mt,
        
                    'somadata04_if':somadata04_if,
                    'somadata04_ip':somadata04_ip,
                    'somadata04_dpg':somadata04_dpg,
                    'somadata04_mt':somadata04_mt,
        
                    'somadata05_if':somadata05_if,
                    'somadata05_ip':somadata05_ip,
                    'somadata05_dpg':somadata05_dpg,
                    'somadata05_mt':somadata05_mt,
        
                    'somadata06_if':somadata06_if,
                    'somadata06_ip':somadata06_ip,
                    'somadata06_dpg':somadata06_dpg,
                    'somadata06_mt':somadata06_mt,
        
                    'somadata07_if':somadata07_if,
                    'somadata07_ip':somadata07_ip,
                    'somadata07_dpg':somadata07_dpg,
                    'somadata07_mt':somadata07_mt,
        
                    'somadata08_if':somadata08_if,
                    'somadata08_ip':somadata08_ip,
                    'somadata08_dpg':somadata08_dpg,
                    'somadata08_mt':somadata08_mt,
        
                    'somadata09_if':somadata09_if,
                    'somadata09_ip':somadata09_ip,
                    'somadata09_dpg':somadata09_dpg,
                    'somadata09_mt':somadata09_mt,
        
                    'somadata10_if':somadata10_if,
                    'somadata10_ip':somadata10_ip,
                    'somadata10_dpg':somadata10_dpg,
                    'somadata10_mt':somadata10_mt,
        
                    'somadata11_if':somadata11_if,
                    'somadata11_ip':somadata11_ip,
                    'somadata11_dpg':somadata11_dpg,
                    'somadata11_mt':somadata11_mt,
        
                    'somadata12_if':somadata12_if,
                    'somadata12_ip':somadata12_ip,
                    'somadata12_dpg':somadata12_dpg,
                    'somadata12_mt':somadata12_mt
            }
        
        datas = {'datas': objeto}
        template_name = 'reports/graphreport.html'
        #messages.warning(request, {somadata07_if})
        return render(request,template_name, datas)
    else:
        messages.warning(request, 'Teste Else no GET!')
        template_name = 'reports/graphreport.html'
        return render(request,template_name,datas)

@login_required
def GraphReportAnual(request):
    #data_start = request.GET['data_start']
    #data_stop = request.GET['data_stop']
    somadata01_if = 0;
    somadata01_ip = 0;
    somadata01_dpg = 0;
    somadata01_mt = 0;

    somadata02_if = 0;
    somadata02_ip = 0;
    somadata02_dpg = 0;
    somadata02_mt = 0;

    somadata03_if = 0;
    somadata03_ip = 0;
    somadata03_dpg = 0;
    somadata03_mt = 0;

    somadata04_if = 0;
    somadata04_ip = 0;
    somadata04_dpg = 0;
    somadata04_mt = 0;

    somadata05_if = 0;
    somadata05_ip = 0;
    somadata05_dpg = 0;
    somadata05_mt = 0;

    somadata06_if = 0;
    somadata06_ip = 0;
    somadata06_dpg = 0;
    somadata06_mt = 0;

    somadata07_if = 0;
    somadata07_ip = 0;
    somadata07_dpg = 0;
    somadata07_mt = 0;

    somadata08_if = 0;
    somadata08_ip = 0;
    somadata08_dpg = 0;
    somadata08_mt = 0;

    somadata09_if = 0;
    somadata09_ip = 0;
    somadata09_dpg = 0;
    somadata09_mt = 0;

    somadata10_if = 0;
    somadata10_ip = 0;
    somadata10_dpg = 0;
    somadata10_mt = 0;

    somadata11_if = 0;
    somadata11_ip = 0;
    somadata11_dpg = 0;
    somadata11_mt = 0;

    somadata12_if = 0;
    somadata12_ip = 0;
    somadata12_dpg = 0;
    somadata12_mt = 0;

    kpi_if01 = 0;
    kpi_ip01 = 0;
    kpi_mt01 = 0;
    kpi_dpg01 = 0;
    kpi_if02 = 0;
    kpi_ip02 = 0;
    kpi_mt02 = 0;
    kpi_dpg02 = 0;
    if 'sigla' in request.GET:
        #https://stackoverflow.com/questions/5895588/django-multivaluedictkeyerror-error-how-do-i-deal-with-it
        if Pch.objects.filter(sigla=request.GET['sigla']).exists():
            pch =  Pch.objects.filter(sigla=request.GET['sigla'])
        else:
            pch = Pch.objects.all()[:random.choice([1, 2, 3, 4])]
    else:
        pch = Pch.objects.all()[:random.choice([1, 2, 3, 4])]
    for x in pch:
        pch_id = x.id
        pch_name = x.pch_name
    if request.method == 'GET':
        if ('data_inicial' in request.GET) and ('data_final' in request.GET):
            format = "%Y-%m-%d %H:%M"
            datestop = request.GET['data_inicial']
            datestop = datetime.datetime.strptime(datestop, format)
            data = Event.objects.filter(data_stop__year=datestop.year, pch_id=pch_id).values('data_start','data_stop','ug','pch_id','interruption')
        else:
            data = Event.objects.filter(data_stop__year=datetime.date.today().year, pch_id=pch_id).values('data_start','data_stop','ug','pch_id','interruption')
        for value in data:
            data_month = value['data_stop']
            data_month = data_month.month
            if data_month == 1:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata01_if
                    else:
                        kpi_if02 +=somadata01_if
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata01_ip
                    else:
                        kpi_ip02 +=somadata01_ip
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata01_mt
                    else:
                        kpi_mt02 +=somadata01_mt
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata01_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata01_dpg
                    else:
                        kpi_dpg02 +=somadata01_dpg
            elif data_month == 2:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata02_if 
                    else:
                        kpi_if02 +=somadata02_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata02_ip 
                    else:
                        kpi_ip02 +=somadata02_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata02_mt 
                    else:
                        kpi_mt02 +=somadata02_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata02_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata02_dpg
                    else:
                        kpi_dpg02 +=somadata02_dpg
            elif data_month == 3:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata03_if 
                    else:
                        kpi_if02 +=somadata03_if                    
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata03_ip 
                    else:
                        kpi_ip02 +=somadata03_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata03_mt 
                    else:
                        kpi_mt02 +=somadata03_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata03_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata03_dpg
                    else:
                        kpi_dpg02 +=somadata03_dpg
            elif data_month == 4:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata04_if 
                    else:
                        kpi_if02 +=somadata04_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata04_ip 
                    else:
                        kpi_ip02 +=somadata04_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata04_mt 
                    else:
                        kpi_mt02 +=somadata04_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata04_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata04_dpg
                    else:
                        kpi_dpg02 +=somadata04_dpg
            elif data_month == 5:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata05_if 
                    else:
                        kpi_if02 +=somadata05_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata05_ip 
                    else:
                        kpi_ip02 +=somadata05_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata05_mt 
                    else:
                        kpi_mt02 +=somadata05_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata05_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata05_dpg
                    else:
                        kpi_dpg02 +=somadata05_dpg
            elif data_month == 6:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata06_if 
                    else:
                        kpi_if02 +=somadata06_if 
                    
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata06_ip 
                    else:
                        kpi_ip02 +=somadata06_ip 
                    kpi_ip += somadata06_ip
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata06_mt 
                    else:
                        kpi_mt02 +=somadata06_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata06_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata06_dpg
                    else:
                        kpi_if02 +=somadata06_dpg
            elif data_month == 7:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata07_if 
                    else:
                        kpi_if02 +=somadata07_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata07_ip 
                    else:
                        kpi_ip02 +=somadata07_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata07_mt 
                    else:
                        kpi_mt02 +=somadata07_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata07_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata07_dpg
                    else:
                        kpi_dpg02 +=somadata07_dpg
            elif data_month == 8:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata08_if 
                    else:
                        kpi_if02 +=somadata08_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata08_ip 
                    else:
                        kpi_ip02 +=somadata08_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata08_mt 
                    else:
                        kpi_mt02 +=somadata08_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata08_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata08_dpg 
                    else:
                        kpi_dpg02 +=somadata08_dpg
            elif data_month == 9:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata09_if 
                    else:
                        kpi_if02 +=somadata09_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata09_ip 
                    else:
                        kpi_ip02 +=somadata09_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata09_mt 
                    else:
                        kpi_mt02 +=somadata09_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata09_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata09_dpg 
                    else:
                        kpi_dpg02 +=somadata09_dpg
            elif data_month == 10:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata10_if 
                    else:
                        kpi_if02 +=somadata10_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata10_ip 
                    else:
                        kpi_ip02 +=somadata10_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata10_mt 
                    else:
                        kpi_mt02 +=somadata10_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata10_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata10_dpg
                    else:
                        kpi_dpg02 +=somadata10_dpg
            elif data_month == 11:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata11_if 
                    else:
                        kpi_if02 +=somadata11_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata11_ip 
                    else:
                        kpi_ip02 +=somadata11_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata11_mt 
                    else:
                        kpi_mt02 +=somadata11_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata11_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata11_dpg
                    else:
                        kpi_dpg02 +=somadata11_dpg
            elif data_month == 12:
                if value['interruption'] == 'IF':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_if += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_if01 +=somadata12_if 
                    else:
                        kpi_if02 +=somadata12_if 
                if value['interruption'] == 'IP':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_ip += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_ip01 +=somadata12_ip 
                    else:
                        kpi_ip02 +=somadata12_ip 
                if value['interruption'] == 'MT':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_mt += (dif.seconds / 60)+(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_mt01 +=somadata12_mt 
                    else:
                        kpi_mt02 +=somadata12_mt 
                if value['interruption'] == 'DPG':
                    dif = value['data_start'] - value['data_stop']
                    somadata12_dpg += (dif.seconds / 60) +(dif.days*24*60);
                    if value['ug'] == 1:
                        kpi_dpg01 +=somadata12_dpg
                    else:
                        kpi_dpg02 +=somadata12_dpg
        objeto   = {
                    'pch_name':pch_name,
                    'kpi_if01':kpi_if01,
                    'kpi_ip01':kpi_ip01,
                    'kpi_mt01':kpi_mt01,
                    'kpi_dpg01':kpi_dpg01,
                    'kpi_if02':kpi_if02,
                    'kpi_ip02':kpi_ip02,
                    'kpi_mt02':kpi_mt02,
                    'kpi_dpg02':kpi_dpg02,
                    'somadata01_if':somadata01_if,
                    'somadata01_ip':somadata01_ip,
                    'somadata01_dpg':somadata01_dpg,
                    'somadata01_mt':somadata01_mt,
        
                    'somadata02_if':somadata02_if,
                    'somadata02_ip':somadata02_ip,
                    'somadata02_dpg':somadata02_dpg,
                    'somadata02_mt':somadata02_mt,
        
                    'somadata03_if':somadata03_if,
                    'somadata03_ip':somadata03_ip,
                    'somadata03_dpg':somadata03_dpg,
                    'somadata03_mt':somadata03_mt,
        
                    'somadata04_if':somadata04_if,
                    'somadata04_ip':somadata04_ip,
                    'somadata04_dpg':somadata04_dpg,
                    'somadata04_mt':somadata04_mt,
        
                    'somadata05_if':somadata05_if,
                    'somadata05_ip':somadata05_ip,
                    'somadata05_dpg':somadata05_dpg,
                    'somadata05_mt':somadata05_mt,
        
                    'somadata06_if':somadata06_if,
                    'somadata06_ip':somadata06_ip,
                    'somadata06_dpg':somadata06_dpg,
                    'somadata06_mt':somadata06_mt,
        
                    'somadata07_if':somadata07_if,
                    'somadata07_ip':somadata07_ip,
                    'somadata07_dpg':somadata07_dpg,
                    'somadata07_mt':somadata07_mt,
        
                    'somadata08_if':somadata08_if,
                    'somadata08_ip':somadata08_ip,
                    'somadata08_dpg':somadata08_dpg,
                    'somadata08_mt':somadata08_mt,
        
                    'somadata09_if':somadata09_if,
                    'somadata09_ip':somadata09_ip,
                    'somadata09_dpg':somadata09_dpg,
                    'somadata09_mt':somadata09_mt,
        
                    'somadata10_if':somadata10_if,
                    'somadata10_ip':somadata10_ip,
                    'somadata10_dpg':somadata10_dpg,
                    'somadata10_mt':somadata10_mt,
        
                    'somadata11_if':somadata11_if,
                    'somadata11_ip':somadata11_ip,
                    'somadata11_dpg':somadata11_dpg,
                    'somadata11_mt':somadata11_mt,
        
                    'somadata12_if':somadata12_if,
                    'somadata12_ip':somadata12_ip,
                    'somadata12_dpg':somadata12_dpg,
                    'somadata12_mt':somadata12_mt
            }
        
        datas = {'datas': objeto}
        template_name = 'reports/graphreport.html'
        return render(request,template_name, datas)
    else:
        messages.warning(request, 'Teste Else no GET!')
        template_name = 'reports/graphreport.html'
        return render(request,template_name,datas)


@register.filter(name='lookup')
def get_item(dictionary, key):
    return dictionary[key]