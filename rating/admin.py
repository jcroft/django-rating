from django.contrib import admin

from rating.models import *

admin.site.register(RatedItem)
admin.site.register(Rating)