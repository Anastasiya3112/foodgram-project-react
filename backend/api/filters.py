from distutils.util import strtobool

from django_filters.rest_framework import FilterSet, filters

from recipes.models import (Ingredient, Recipe, FavoriteRecipe,
                            ShoppingList, Tag)

CHOICES_LIST = (
    ('0', 'False'),
    ('1', 'True')
)


class IngredientFilters(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilters(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    author = filters.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    is_favorited = filters.ChoiceFilter(
        method='is_favorited_filter',
        choices=CHOICES_LIST
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter',
        choices=CHOICES_LIST
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorite = FavoriteRecipe.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in favorite]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_list = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_list]
        new_queryset = queryset.filter(id__in=recipes)

        if not strtobool(value):
            return queryset.difference(new_queryset)

        return queryset.filter(id__in=recipes)
