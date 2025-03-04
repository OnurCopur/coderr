from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            "review_count": 10,
            "average_rating": 4.6,
            "business_profile_count": 45,
            "offer_count": 150
        }
        return Response(data)