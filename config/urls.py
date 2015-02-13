from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.autodiscover()

'''
direct to template
'''
class DirectTemplateView(TemplateView):
    extra_context = None
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context


urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('questionapp.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout',  {'next_page': '/'}, name="logout"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="account_login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',  {'next_page': '/'}, name="account_logout"),

    #url(r'^accounts/', include('allauth.urls')),
    #url(r'^badges/', include('badger.urls')),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
