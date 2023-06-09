from django_filters.rest_framework import filters

from recipes.models import Ingredient


class IngredientFilters(filters.SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_favorited = request.query_params.get('is_favorited')
        is_in_shopping_cart = request.query_params.get(
            'is_in_shopping_cart'
        )
        recipes_author = request.query_params.get('author')
        recipes_tags = request.query_params.getlist('tags')
        new_queryset = queryset
        if is_favorited == '1':
            new_queryset = new_queryset.filter(
                favorites__user=request.user
            )
        if is_in_shopping_cart == '1':
            new_queryset = new_queryset.filter(
                shopping_list__user=request.user
            )
        if recipes_author is not None:
            new_queryset = new_queryset.filter(
                author=recipes_author
            )
        if recipes_tags:
            regular_tags = '|'.join(recipes_tags)
            new_queryset = new_queryset.filter(
                tags__slug__regex=regular_tags
            )
        return new_queryset.distinct()
