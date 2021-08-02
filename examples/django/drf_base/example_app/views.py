from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def root(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 42")
            result = cursor.fetchall()
        db_message = f"{result} - was fetched from PostgreSQL"
    except Exception as e:
        db_message = f"Couldn't connect to db ({e})"
    return Response({"message": "Hello, from Yappa!",
                     "message from db": db_message})
