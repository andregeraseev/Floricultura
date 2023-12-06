from django.urls import path
from .view import  login_view, user_login, logout_view, UserRegistrationView, AddressRegistrationView
user_register = UserRegistrationView.as_view()
address_register =AddressRegistrationView.as_view()
urlpatterns = [

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user_login/', user_login, name='user_login'),
    path('cadastro/', user_register, name='cadastro'),
    path('endereco/', address_register, name='address_register'),


]



