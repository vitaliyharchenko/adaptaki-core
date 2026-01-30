from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tasks.domain.enums import TaskType


class TaskTypesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает список типов заданий.

        Пример ответа:
            {
              "task_types": [{"value": "short_text", "label": "Короткий ответ"}]
            }
        """
        return Response(
            {
                "task_types": [
                    {"value": task_type.value, "label": task_type.label()}
                    for task_type in TaskType
                ]
            }
        )
