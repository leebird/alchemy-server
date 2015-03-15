from .website import web_urlpatterns
from .api import api_urlpatterns

urlpatterns = web_urlpatterns + api_urlpatterns
