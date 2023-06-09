from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe


class IngredientFilters(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
    tags = filters.CharFilter(
        field_name='tags__slug',
        method='tags_filter'
    )
    is_favorited = filters.CharFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.CharFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def tags_filter(self, queryset, slug, tags):
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def is_favorited_filter(self, queryset, is_favorited, slug):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        is_favorited = self.request.query_params.get('is_favorited', )
        if is_favorited:
            return queryset.filter(
                favorites__user=self.request.user
            ).distinct()
        return queryset

    def is_in_shopping_list_filter(self, queryset, is_in_shopping_cart, slug):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart',
        )
        if is_in_shopping_cart:
            return queryset.filter(
                shopping_list__user=self.request.user
            ).distinct()
        return queryset
