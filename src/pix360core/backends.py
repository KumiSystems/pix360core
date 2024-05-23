from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class OIDCBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        email = claims.get("email")
        return self.UserModel.objects.create_user(email)

    def get_username(self, claims):
        return claims.get("email")
