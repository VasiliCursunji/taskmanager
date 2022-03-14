from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated



class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    # def post(self, request):
    #     # user_info = request.data
    #     serialized_user = UserSerializer(data=request.data)
    #     if serialized_user.is_valid():
    #         new_user = serialized_user.save()
    #         new_user.set_password(new_user.password)
    #         new_user.save()
    #         return Response(new_user, status=status.HTTP_201_CREATED)
    #     return Response(serialized_user.errors)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            is_superuser=True
        )
        user.set_password(validated_data['password'])
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()