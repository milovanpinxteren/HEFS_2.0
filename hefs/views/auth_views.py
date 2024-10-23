import time

from django.db.models import Q
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth import logout

class LogoutView(View):
    def get(self, request):
        print('logout')
        request.session.flush()
        logout(request)
        return redirect('login')
        # return render(request, 'login.html')




class CustomLoginView(DefaultLoginView):
    def form_valid(self, form):
        if form.is_valid():
            print('valid')
            response = super().form_valid(form)
            current_user = form.get_user().id
            redirect_url = reverse('index')
            return redirect(redirect_url)
        else:
            return super().form_invalid(form)



class ChangePasswordView(View):
    template_name = 'change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email_or_username = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        if not (email_or_username and old_password and new_password):
            context = {'message': _('all_fields_are_required')}
            return render(request, self.template_name, context)
        try:
            user = User.objects.get(Q(username=email_or_username) | Q(email=email_or_username))
        except User.DoesNotExist:
            context = {'message': _('username_or_email_not_known')}
            return render(request, self.template_name, context)

        if not user.check_password(old_password):
            context = {'message': _('incorrect_old_password')}
            return render(request, self.template_name, context)
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            context = {'error_messages': e.messages}
            return render(request, self.template_name, context)

        user.set_password(new_password)
        user.save()
        return render(request, 'succesfull_password_change.html')
