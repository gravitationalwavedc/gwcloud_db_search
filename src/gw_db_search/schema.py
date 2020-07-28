import graphene
import db_search.schema


class Query(db_search.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
