from rest_framework.views import APIView
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from celery.result import AsyncResult
from .tasks import generate_mockup_task
from .models import Mockup
from .serializers import MockupSerializer
from rest_framework import generics, permissions, filters
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "example": "Hello World"},
                "font": {"type": "string", "example": "vazir"},
                "text_color": {"type": "string", "example": "#FFFFFF"},
                "shirt_color": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["white", "black"]
                },
            },
            "required": ["text"]
        }
    },
    responses={
        202: OpenApiResponse(description="Mockup generation started (Celery task created)"),
        400: OpenApiResponse(description="Invalid input")
    },
    description="Create a Celery task to generate a mockup"
)
class GenerateMockupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get('text')
        font = request.data.get('font', 'arial')
        text_color = request.data.get('text_color', '#000000')
        shirt_colors = request.data.get('shirt_color', ['white'])

        if not isinstance(shirt_colors, list):
            shirt_colors = [shirt_colors]

        task_ids = []
        for color in shirt_colors:
            mockup = Mockup.objects.create(
                user=request.user,
                text=text,
                font=font,
                text_color=text_color,
                shirt_color=color
            )
            task = generate_mockup_task.delay(mockup.id)
            task_ids.append(task.id)

        return Response({
            "task_ids": task_ids,
            "status": "PENDING",
            "message": "Image generation started..."
        }, status=status.HTTP_202_ACCEPTED)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='task_id',
            type={'type': 'string', 'format': 'uuid'},
            location=OpenApiParameter.PATH,
            required=True,
            description='UUID of the Celery task'
        )
    ],
    responses={
        200: OpenApiResponse(description="Task status and results"),
        404: OpenApiResponse(description="Task not found"),
    },
    description="Check the status and results of a Celery task"
)
class TaskStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id):
        result = AsyncResult(str(task_id))
        response = {"task_id": task_id, "status": result.status}

        if result.ready() and isinstance(result.result, dict):
            response["results"] = [result.result]

        return Response(response)

class MockupListView(generics.ListAPIView):
    serializer_class = MockupSerializer
    permission_classes = [permissions.IsAuthenticated]

        # فعال‌سازی Search و Ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # فیلدهایی که قابل جستجو هستند
    search_fields = ['text', 'shirt_color', 'font']

    # مرتب‌سازی پیش‌فرض و فیلدهای مجاز برای ordering
    ordering_fields = ['created_at', 'shirt_color', 'font']
    ordering = ['-created_at']

    def get_queryset(self):
        return Mockup.objects.filter(user=self.request.user).order_by('-created_at')
