from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

@login_required
def ChangePassword(request):
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