from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilters(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='tags',
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
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(
            favorites__user=self.request.user
        )

    def is_in_shopping_list_filter(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return Recipe.objects.filter(
                shopping_list__user=self.request.user
            )
        return queryset
