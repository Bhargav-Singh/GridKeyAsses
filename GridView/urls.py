"""
URL configuration for GridView project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
#
# schema_view = get_schema_view(
#    openapi.Info(
#       title="Stock Market Project API",
#       default_version='v1',
#       description="API documentation for the Stock Market Project",
#       terms_of_service="https://www.example.com/terms/",
#       contact=openapi.Contact(email="contact@example.com"),
#       license=openapi.License(name="MIT License"),
#    ),
#    public=True,
# )

urlpatterns = [
    path('api/users/', include('users.urls')),
    path('api/trades/', include('trades.urls')),
    # Swagger UI:
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # # ReDoc UI (optional):
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
