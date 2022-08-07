from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import text
# Register your models here.

@admin.register(text)
class textAdmin(ImportExportModelAdmin):
    pass