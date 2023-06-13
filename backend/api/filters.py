from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


User = get_user_model()


class IngredientFilters(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(method='get_is_favorited')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'author',
            'is_in_shopping_cart',
            'tags'
        )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                favorites__user=self.request.user
            )
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_list__user=self.request.user
            )
        return Recipe.objects.all()
