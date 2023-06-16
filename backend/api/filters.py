from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilters(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter',
        label='favorite',
    )
    is_in_shopping_list = filters.BooleanFilter(
        method='is_in_shopping_list_filter',
        label='shoppings_list',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_list')

    def is_favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(
            favorites__user=self.request.user
        )

    def is_in_shopping_list_filter(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_list__user=self.request.user
            )
