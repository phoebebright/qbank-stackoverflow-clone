from django.contrib import admin
from questionapp.models import *

admin.site.register(QUser)
admin.site.register(Question)
admin.site.register(Answer)