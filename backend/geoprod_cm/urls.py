from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regions', views.RegionViewSet)
router.register(r'departements', views.DepartementViewSet)
router.register(r'arrondissements', views.ArrondissementViewSet)
router.register(r'productions', views.ProductionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
]