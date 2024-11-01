from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Register your models here.

class CategoryMasterResources(resources.ModelResource):
    class Meta:
        model = models.CategoryMaster

class CategoryMasterAdmin(ImportExportModelAdmin):
    resource_class = CategoryMasterResources

class IventsResources(resources.ModelResource):
    class Meta:
        model = models.Ivents

class IventsAdmin(ImportExportModelAdmin):
    resource_class = IventsResources



admin.site.register(models.CategoryMaster, CategoryMasterAdmin)
admin.site.register(models.Ivents, IventsAdmin)



