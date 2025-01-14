"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from hefs.forms import CustomAuthenticationForm
from hefs.views.auth_views import CustomLoginView, LogoutView, ChangePasswordView

from . import views

urlpatterns = [
                  path('', views.index, name='index'),
                  path('hefs/', include('hefs.urls')),
                  path('admin/', admin.site.urls),
                  path('login', CustomLoginView.as_view(template_name='login.html',
                                                        authentication_form=CustomAuthenticationForm), name='login'),
                  path('logout', LogoutView.as_view(), name='logout'),
                  path('show_change_password_page', ChangePasswordView.as_view(), name='show_change_password_page'),
                  path('change_password', ChangePasswordView.as_view(), name='change_password'),
                  path('track_order', views.track_order, name='track_order'),
                  path('get_terminal_for_user', views.get_terminal_for_user, name='get_terminal_for_user'),
                  path('get_product_fees', views.get_product_fees, name='get_product_fees'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
