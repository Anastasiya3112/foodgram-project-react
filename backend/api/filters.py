from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class IngredientFilters(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset.exclude(
            in_favorites__user=self.request.user
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_list__user=self.request.user
            )
