from django.conf.urls.defaults import *

from rating.views import *

urlpatterns = patterns('',
  url(
    regex   = r'^rate/$',
    view    = rate,
    name    = 'rate',
    ),
)
