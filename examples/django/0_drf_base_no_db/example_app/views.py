from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def root(request):
    return Response({"message": "Hello, from Yappa!",
                     "next step": "go to the next example: "
                                  "connect you managed Postgresql!"})
