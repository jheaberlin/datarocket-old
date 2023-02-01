from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("sign_in", views.logIn, name="login"),
    path("sign_up", views.signup, name="signup"),
    path("", views.activity, name="home"),
    path("logout", views.signOut, name="logout"),
    path("create_push/<page>", views.createPush, name="createPush"),
    path("create_endpoint/<page>", views.createEndpoint, name="createEndpoint"),
    path("delete_push/<id>", views.deletePush, name="deletePush"),
    path("delete_endpoint/<id>", views.deleteEndpoint, name="deleteEndpoint"),
    path("launches", views.pushes, name="launches"),
    path("endpoints", views.endpoints, name="endpoints"),
    path('stripe_checkout', views.stripe_checkout, name='stripe_checkout'),
    path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
    path('create_portal_session', views.create_portal_session, name='create_portal_session'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
