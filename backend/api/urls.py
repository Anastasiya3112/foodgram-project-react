from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AuthToken, IngredientViewSet, RecipeViewSet, TagViewSet,
                    UserViewSet, FavoriteCreateAPIView,
                    FavoriteDeleteAPIView)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, 'users')
router_v1.register('tags', TagViewSet, 'tags')
router_v1.register('ingredients', IngredientViewSet, 'ingredients')
router_v1.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('favorites/', FavoriteCreateAPIView.as_view(),
         name='create_favorite'),
    path('favorites/<int:pk>/', FavoriteDeleteAPIView.as_view(),
         name='delete_favorite'),
]
