from django.contrib import admin
from apps.data.models import *
# Register your models here.
admin.site.register(AhuinHereglegch)
admin.site.register(CallType)
admin.site.register(AanAngilal)
class DedstantsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
admin.site.register(DedStants, DedstantsAdmin)
admin.site.register(Bank)
admin.site.register(Cycle)
admin.site.register(ChartData)
admin.site.register(TechnicalProposal)
class CustomerAdmin(admin.ModelAdmin):
       list_display = ('code', 'first_name', 'last_name')
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Address)
admin.site.register(Aimag)
admin.site.register(Duureg)
admin.site.register(Horoo)
admin.site.register(Block)
admin.site.register(Hothon)
admin.site.register(CallSubType)
admin.site.register(CallGeneralType)
admin.site.register(Tooluur)
class TooluurCustomerAdmin(admin.ModelAdmin):
       list_display = ('tooluur_id', 'customer_code', 'created_date')
admin.site.register(TooluurCustomer, TooluurCustomerAdmin)
admin.site.register(Transformator)
admin.site.register(PriceTariff)

class BichiltAdmin(admin.ModelAdmin):
       list_display = ('created_date', 'tooluur', 'bichilt_date', 'total_diff')
admin.site.register(Bichilt, BichiltAdmin)
admin.site.register(TulburtUilchilgee)
admin.site.register(Avlaga)
admin.site.register(Salgalt)
admin.site.register(AlbanTushaal)
admin.site.register(Zaavarchilgaa)
class TasraltAdmin(admin.ModelAdmin):
    list_display = ('ded_stants', 'tasarsan_tonoglol', 'tasarsan_date', 'zalgasan_date')
admin.site.register(TooluurMark)
admin.site.register(Amper)
admin.site.register(Voltage)
admin.site.register(TransformatorMark)