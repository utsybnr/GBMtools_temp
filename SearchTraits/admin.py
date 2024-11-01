from django.contrib import admin
from . import models
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Register your models here.

class ConditionResources(resources.ModelResource):
    class Meta:
        model = models.Condition
        
class ConditionAdmin(ImportExportModelAdmin):
    resource_class = ConditionResources

admin.site.register(models.Condition, ConditionAdmin)

class ConditionFilterResources(resources.ModelResource):
    class Meta:
        model = models.ConditionFilter

class ConditionFilterAdmin(ImportExportModelAdmin):
    resource_class = ConditionFilterResources

admin.site.register(models.ConditionFilter, ConditionFilterAdmin)

class EffectFilterResources(resources.ModelResource):
    class Meta:
        model = models.EffectFilter

class EffectFilterAdmin(ImportExportModelAdmin):
    resource_class = EffectFilterResources

admin.site.register(models.EffectFilter, EffectFilterAdmin)

class EffectResources(resources.ModelResource):
    class Meta:
        model = models.Effect

class EffectAdmin(ImportExportModelAdmin):
    resource_class = EffectResources

admin.site.register(models.Effect, EffectAdmin)

class PartResources(resources.ModelResource):
    class Meta:
        model = models.Part

class PartAdmin(ImportExportModelAdmin):
    resource_class = PartResources

admin.site.register(models.Part, PartAdmin)

class WordTagResources(resources.ModelResource):
    class Meta:
        model = models.WordTag

class WordTagAdmin(ImportExportModelAdmin):
    resource_class = WordTagResources

admin.site.register(models.WordTag, WordTagAdmin)


