import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import UserProfile


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email",)


class UserProfileType(DjangoObjectType):
    class Meta:
        model = UserProfile
        fields = ("id", "bio", "avatar", "user")


class AccountsQuery(graphene.ObjectType):
    me = graphene.Field(UserType)
    my_profile = graphene.Field(UserProfileType)

    def resolve_me(self, info):
        user = info.context.user
        return user if user.is_authenticated else None

    def resolve_my_profile(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return None
        return getattr(user, 'profile', None)


class UpdateProfile(graphene.Mutation):
    class Arguments:
        bio = graphene.String(required=False)

    ok = graphene.Boolean()
    profile = graphene.Field(UserProfileType)

    @classmethod
    def mutate(cls, root, info, bio=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if bio is not None:
            profile.bio = bio
        profile.save()
        return UpdateProfile(ok=True, profile=profile)


class AccountsMutation(graphene.ObjectType):
    update_profile = UpdateProfile.Field()


class Register(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=False)
        password = graphene.String(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, username, password, email=None):
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise Exception("Username already taken")
        user = User.objects.create_user(username=username, email=email or "", password=password)
        return Register(ok=True, user=user)


class AccountsMutation(graphene.ObjectType):
    update_profile = UpdateProfile.Field()
    register = Register.Field()


