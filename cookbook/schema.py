import graphene
import ingredients.schema


class Query(ingredients.schema.RelayQuery,ingredients.schema.Query,graphene.ObjectType):
    pass

class Mutation(ingredients.schema.Mutation,graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query,mutation=Mutation)