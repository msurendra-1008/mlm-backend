from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ProtectedView(APIView):
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        return Response({
            "message": "This is a protected view.",
            "user": request.user.username,
            "mobile": request.user.mobile
        })


class PublicView(APIView):
    def get(self, request):
        return Response({
            "message": "This is a public view."
        })