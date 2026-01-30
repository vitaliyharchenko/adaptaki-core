from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.graph.models import Subject


class SubjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает список предметов.

        Пример ответа:
            {
              "subjects": [{"id": 1, "title": "Математика"}]
            }
        """
        subjects = Subject.objects.order_by("title").values("id", "title")
        return Response({"subjects": list(subjects)})
