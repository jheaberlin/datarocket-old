from django.contrib import admin
from .models import endpoint, push, batch

admin.site.register(endpoint)
admin.site.register(push)
admin.site.register(batch)