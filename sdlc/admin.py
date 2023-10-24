from django.contrib import admin

from .models import Permission,fhirip,Document
admin.site.register(Permission)
admin.site.register(fhirip)
admin.site.register(Document)