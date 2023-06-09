from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.filters import RecipeFilters, IngredientFilters
from api.pagination import LimitPageNumberPagination
from api.permissions import UserPermission
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, RecipeSmallSerializer,
                             TagSerializer, TokenSerializer,
                             UserFollowSerializer, UserSerializer)
from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingList, Tag)
from users.models import Follow, User


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    @action(methods=('POST', 'DELETE'), detail=True)
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if self.request.method == 'POST':
            serializer = UserFollowSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserFollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class AuthToken(ObtainAuthToken):

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        auth_token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': auth_token.key},
            status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (UserPermission, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (UserPermission, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilters
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (UserPermission, )
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def create_method(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'Ошибка': 'Данный рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSmallSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_method(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            model.objects.filter(user=user, recipe__id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'Ошибка': 'Данный рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('POST', 'DELETE'),
            detail=True)
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_method(ShoppingList, request.user, pk)
        return self.delete_method(ShoppingList, request.user, pk)

    @action(methods=('POST', 'DELETE'),
            detail=True)
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_method(FavoriteRecipe, request.user, pk)
        return self.delete_method(FavoriteRecipe, request.user, pk)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        user = self.request.user
        shopping_list = user.shopping_list.all()
        data = {}
        for point in shopping_list:
            recipe = point.recipe
            ingredients = AmountIngredient.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if name not in data:
                    data[name] = {"measurement_unit": measurement_unit,
                                  "amount": amount}
                else:
                    data[name]["amount"] = (data[name]["amount"] + amount)
        shoppinglist = []
        for name, data in data.items():
            shoppinglist.append(
                f"{name} - {data['amount']} {data['measurement_unit']},\n"
            )
        response = HttpResponse(shoppinglist, content_type='text/plain')
        return response
