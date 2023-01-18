from django.contrib import admin

# Register your models here.
from .models import (Automobilis,
                     AutomobilioModelis,
                     Paslauga,
                     Uzsakymas,
                     UzsakymoEilute)


class UzsakymoEiluteInLine(admin.TabularInline):
    model = UzsakymoEilute
    extra = 0

class UzsakymasAdmin(admin.ModelAdmin):
    inlines = [UzsakymoEiluteInLine]

admin.site.register(Automobilis)
admin.site.register(AutomobilioModelis)
admin.site.register(Paslauga)
admin.site.register(Uzsakymas, UzsakymasAdmin)
admin.site.register(UzsakymoEilute)
