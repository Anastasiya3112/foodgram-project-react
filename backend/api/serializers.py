from django.contrib.auth import authenticate
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField

from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingList, Tag)
from users.models import User, Follow


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSmallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return request.user.is_authenticated and obj.following.filter(
            user=request.user).exists()


class UserFollowSerializer(UserSerializer):

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSmallSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        write_only=True,
        label='Email')
    password = serializers.CharField(
        write_only=True,
        label='Пароль',
        style={'input_type': 'password'})
    auth_token = serializers.CharField(
        read_only=True,
        label='Токен')

    def validate(self, value):
        email = value.get('email')
        password = value.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password)
        else:
            raise serializers.ValidationError(
                detail='Укажите еmail и пароль.',
                code='authorization')
        value['user'] = user
        return value


class AmountsIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountsIngredientSerializer(
        many=True,
        source='recipe')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',
                  )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated and FavoriteRecipe.objects.filter(
                user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingList.objects.filter(user=user, recipe=recipe).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):

    ingredients = IngredientRecipeSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)

    def validate_tag(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    detail='Указанного тэга не существует')
        return tags

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                detail='Должен быть хотя бы один ингредиент')
        for ingredient in ingredients:
            value = ingredient['id']
            if value in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны')
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    detail='Количество ингредиента должно быть больше 1')
        return ingredients

    def validate_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                detail='Время приготовления должно быть не меньше 1 минуты!')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        ingredients_recipe = []
        for ingredient in ingredients:
            ingredients_recipe.append(
                AmountIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        AmountIngredient.objects.bulk_create(ingredients_recipe)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        request = self.context.get('request', None)
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(validated_data.get('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже есть в избранном.'
            )
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в корзину.'
            )
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
