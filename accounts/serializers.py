from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = 'university_id'

    def validate(self, attrs):
        data = super().validate(attrs)

        # نضيف معلومات المستخدم للـ response
        data['user'] = {
            'id': self.user.id,
            'university_id': self.user.university_id,
            'role': self.user.role,
            'username': self.user.username,
        }

        return data