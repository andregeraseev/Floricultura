"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from setup.view import home, department_detail, category_detail, search, search_view, dashboard_graficos
from banners.views import track_click
from tiny_webhook.view import ProductWebhook
from tiny_webhook.estoque_tiny import tiny_webhook_stock_update
from importador.view import upload_csv,upload_csv_for_userprofile, upload_csv_for_address,upload_csv_for_orders
from django.contrib.auth import views as auth_views
from usuario.view import verificar_email

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('carrinho/', include('carrinho.urls')),
    path('usuario/', include('usuario.urls')),
    path('checkout/', include('pedidos.urls')),
    path('produtos/', include('products.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('favoritos/', include('favoritos.urls')),
    path('avise/', include('avise.urls')),
    path('blog/', include('blog.urls')),

    path('search/<str:q>', search, name='search'),
    path('search_view/<str:q>', search_view, name='search'),
    path('importador', upload_csv, name='importador'),
    path('importador_usuario', upload_csv_for_userprofile, name='importador_usuario'),
    path('importador_endereco', upload_csv_for_address, name='importador_endereco'),
    path('importador_pedidos', upload_csv_for_orders, name='importador_pedidos'),

    # path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('department/<slug:slug>/', department_detail, name='department_detail'),
    path('category/<slug:slug>/', category_detail, name='category_detail'),
    # path('add_to_cart/', add_to_cart, name='add_to_cart'),
    # path('delete_item_cart/', delete_item_cart, name='delete_item_cart'),





    # WEBHOOKS
    path('webhook/tiny_produtos/' , ProductWebhook.as_view(), name='product-webhook'),
    path('webhook/tiny_webhook_stock_update/' , tiny_webhook_stock_update, name='tiny_webhook_stock_update'),

    # path('webhook/envia_pedido/' , envia_pedido, name='envia_pedido'),

#     TRACKING BANNER
    path('track-click/<int:banner_id>/<str:banner_type>/', track_click, name='track-click'),

# resetpassword
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('usuario/', include('django.contrib.auth.urls')),
    path('verificar_email/', verificar_email, name='verificar_email'),

#dashboard
    path('painel/', dashboard_graficos, name='dashboard_graficos'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)