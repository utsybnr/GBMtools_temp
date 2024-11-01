from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class UnitResources(resources.ModelResource):
    class Meta:
        model = models.Unit
        
class UnitAdmin(ImportExportModelAdmin):
    resource_class = UnitResources

admin.site.register(models.Unit, UnitAdmin)

class StatusResources(resources.ModelResource):
    class Meta:
        model = models.Status
        
class StatusAdmin(ImportExportModelAdmin):
    resource_class = StatusResources

admin.site.register(models.Status, StatusAdmin)