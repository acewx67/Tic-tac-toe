from django.contrib import admin
from . models import Array
# Register your models here.
@admin.register(Array)
class ArrayAdmin(admin.ModelAdmin):
    list_display = ['data']