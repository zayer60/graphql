import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import *
import django_filters


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")
        filter_fields = ['name', 'ingredients']
        interfaces = (graphene.relay.Node,)


class IngredientNode(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        interfaces = (graphene.relay.Node,)


class RelayQuery(graphene.ObjectType):
    category = graphene.relay.Node.Field(CategoryNode)
    all_category = DjangoFilterConnectionField(CategoryNode)

    ingredient = graphene.relay.Node.Field(IngredientNode)
    all_ingredient = DjangoFilterConnectionField(IngredientNode)


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "ingredients")
        interfaces = (graphene.relay.Node,)


class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "notes", "category")


class Query(graphene.ObjectType):
    all_ingredients = graphene.List(IngredientType)
    get_category = graphene.Field(CategoryType, name=graphene.String(required=True))

    def resolve_all_ingredients(root, info):
        return Ingredient.objects.select_related("category").all()

    def resolve_get_category(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None


class CategoryInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String(required=True)


class CreateCategory(graphene.Mutation):
    class Arguments:
        category_data = CategoryInput(required=True)

    category = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, category_data=None):
        category = Category(name=category_data.name)
        category.save()
        return CreateCategory(category=category)


class UpdateCategory(graphene.Mutation):
    class Arguments:
        category_data = CategoryInput(required=True)
        # id = graphene.ID()
        # name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, category_data=None):
        category = Category.objects.get(id=category_data.id)
        category.name = category_data.name
        category.save()
        return UpdateCategory(category=category)


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    category = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, id):
        category = Category.objects.get(id=id)
        category.delete()
        return DeleteCategory(category=category)


class IngredientInputs(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    notes = graphene.String()
    category_id = graphene.ID()


class CreateIngredient(graphene.Mutation):
    class Arguments:
        ingredient_data = IngredientInputs(required=True)

    ing = graphene.Field(IngredientType)

    @classmethod
    def mutate(cls, root, info, ingredient_data=None):
        category = Category.objects.get(id=ingredient_data.category_id)
        ing = Ingredient.objects.create(name=ingredient_data.name, notes=ingredient_data.notes,
                                        category=category)
        # ing = Ingredient(name=ingredient_data.name, notes=ingredient_data.notes, category=category)
        # ing.save()
        return CreateIngredient(ing=ing)


class UpdateIngredient(graphene.Mutation):
    class Arguments:
        ingredient_data = IngredientInputs()

    ing = graphene.Field(IngredientType)

    @classmethod
    def mutate(cls, root, info, ingredient_data=None):
        category = Category.objects.get(id=ingredient_data.category_id)
        ing = Ingredient.objects.get(id=ingredient_data.id)
        ing.name = ingredient_data.name
        ing.notes = ingredient_data.notes
        ing.category = category
        ing.save()
        return UpdateIngredient(ing=ing)


class DeleteIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    ing = graphene.Field(IngredientType)

    @classmethod
    def mutate(cls, root, info, id):
        ing = Ingredient.objects.get(id=id)
        ing.delete()
        return DeleteIngredient(ing=ing)


class RelayCreateIngredient(graphene.ClientIDMutation):
    class Input:
        ingredient_data = IngredientInputs(required=True)

    ing = graphene.Field(IngredientNode)

    def mutate_and_get_payload(root, info, ingredient_data=None):
        category = Category.objects.get(id=ingredient_data.category_id)
        ing = Ingredient.objects.create(name=ingredient_data.name, notes=ingredient_data.notes,
                                        category=category)
        # ing = Ingredient(name=ingredient_data.name, notes=ingredient_data.notes, category=category)
        # ing.save()
        return CreateIngredient(ing=ing)


class Mutation(graphene.ObjectType):
    updateCategory = UpdateCategory.Field()
    createCategory = CreateCategory.Field()
    deleteCategory = DeleteCategory.Field()
    createIngredient = CreateIngredient.Field()
    updateIngredient = UpdateIngredient.Field()
    deleteIngredient = DeleteIngredient.Field()
    relayCreateIngredient = RelayCreateIngredient.Field()
