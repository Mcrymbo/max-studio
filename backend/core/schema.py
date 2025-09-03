import graphene
import graphql_jwt
from accounts.schema import AccountsQuery, AccountsMutation
from videos.schema import VideosQuery, VideosMutation


class Query(AccountsQuery, VideosQuery, graphene.ObjectType):
    healthcheck = graphene.String(description="Basic healthcheck")

    def resolve_healthcheck(self, info):
        return "ok"


class Mutation(AccountsMutation, VideosMutation, graphene.ObjectType):
    # JWT auth
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


