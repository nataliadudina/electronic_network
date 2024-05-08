from django.contrib import admin

from networks.models import NetworkNode, Product, Contacts


class SupplierInline(admin.TabularInline):
    """ Отображает дополнительные сведения о клиентах в карточке организации """
    model = NetworkNode
    extra = 1
    verbose_name = "Client"
    verbose_name_plural = "Clients"


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    fields = ('name', 'level', 'supplier', 'debt_amount', 'creation_time')
    list_display = ('id', 'name', 'level', 'supplier', 'debt_amount')
    readonly_fields = ('contacts', 'products', 'creation_time')
    list_display_links = ('id', 'name', 'supplier')
    search_fields = ('name', 'contacts__city')
    list_filter = ('level', 'contacts__country', 'debt_amount')
    actions = ('zero_out_debt',)
    ordering = ('name',)
    list_per_page = 10
    inlines = [SupplierInline]

    @admin.action(description='Clear the debt of selected customers')
    def zero_out_debt(self, request, queryset):
        queryset.update(debt_amount=0.00)
        self.message_user(request, f'The debt was set to zero.')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'model', 'release_date')
    readonly_fields = ('sales_channel',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('sales_channel__name',)
    ordering = ('name',)
    list_per_page = 10


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('id', 'network_node',  'email', 'department', 'country', 'city', 'street', 'building')
    readonly_fields = ('network_node',)
    list_display_links = ('id', 'network_node')
    search_fields = ('network_node__name',)
    list_filter = ('country', 'city')
    ordering = ('network_node',)
    list_per_page = 10
