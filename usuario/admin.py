from django.contrib import admin
from .models import UserProfile, Address, UserLoginHistory, UserPageVisit


from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Desregistra o modelo User padrão
admin.site.unregister(User)

# Extende a classe UserAdmin padrão para adicionar o ID do usuário
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'profile', 'email', 'first_name', 'last_name', 'is_staff')  # Adicione 'id' aqui
    # Se você quiser adicionar o 'id' a outras seções como search_fields, list_filter, etc., também pode fazer isso.

# Registra novamente o modelo User com a nova classe UserAdmin
admin.site.register(User, UserAdmin)
# Configuração para UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'cpf', 'phone_number', 'whatsapp', 'birth_date', 'age', 'loyalty_points', 'newsletter')
    search_fields = ('user__username', 'cpf', 'phone_number')
    list_filter = ('gender', 'newsletter')

    @admin.display(description='Age')
    def age(self, obj):
        return obj.age

# Configuração para Address
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'session','full_address', 'is_primary')
    search_fields = ('user_profile__user__username', 'street', 'city', 'state', 'zipcode')
    list_filter = ('is_primary', 'pais')

# Configuração para UserLoginHistory
class UserLoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'ip_address', 'login_time', 'time_since_login')
    search_fields = ('user_profile__user__username', 'ip_address')
    list_filter = ('login_time',)

# Configuração para UserPageVisit
class UserPageVisitAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'url', 'timestamp')
    search_fields = ('user_profile__user__username', 'url')
    list_filter = ('timestamp',)

# Registrar os modelos e suas configurações no admin
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserLoginHistory, UserLoginHistoryAdmin)
admin.site.register(UserPageVisit, UserPageVisitAdmin)
