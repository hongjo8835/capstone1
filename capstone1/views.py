from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = RefreshToken(request.data['refresh'])

        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)

        return response
