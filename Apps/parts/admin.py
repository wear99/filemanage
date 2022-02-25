from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.PartCode)
admin.site.register(models.ArchiveBom)

admin.site.register(models.ErpBom)
admin.site.register(models.PartCost)


