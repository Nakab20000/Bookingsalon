# serializers.py
from rest_framework import serializers
from .models import CustomUser
from rest_framework import serializers
from .models import Portfolio
from .models import Booking
from .models import Promotion
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirmation', 'phone_number', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "first_name", "last_name","profile_image"]
        read_only_fields = ["username"]  # ✅ ห้ามแก้ไข username


class PortfolioSerializer(serializers.ModelSerializer):
    image1 = serializers.ImageField(required=False, allow_null=True)
    image2 = serializers.ImageField(required=False, allow_null=True)
    image3 = serializers.ImageField(required=False, allow_null=True)
    image4 = serializers.ImageField(required=False, allow_null=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'image1', 'image2', 'image3', 'image4', 'user']

    def create(self, validated_data):
        # ข้อมูลที่ได้จาก request.data จะถูกจัดเก็บใน validated_data
        portfolio = Portfolio.objects.create(**validated_data)
        return portfolio

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name']  # สามารถเลือกฟิลด์ที่ต้องการได้


class BookingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    stylist_name = serializers.CharField(source="stylist.username", read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'username', 'booking_date', 'booking_time',
            'hair_style', 'hair_type', 'status', 'promotion', 'price', 'stylist', 'stylist_name', 'cancel_reason'
        ]
        read_only_fields = ['id', 'user', 'username', 'status', 'cancel_reason']

    def to_representation(self, instance):
        instance.update_status()  # ✅ อัปเดตสถานะก่อนคืนค่า
        return super().to_representation(instance)




class UpdateBookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']

class PromotionSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            'promotion_id',
            'name',
            'description',
            'discount_amount',
            'discount_type',
            'start_date',
            'end_date',
            'is_active',
            'status',
            'final_price'  # ✅ เพิ่มราคาหลังคำนวณส่วนลด
        ]

    def get_final_price(self, obj):
        # สมมติราคาต้นทางคือ 120 (หรือจะรับจาก context ก็ได้)
        original_price = 120  
        if obj.discount_type == 'percent':
            discount = (obj.discount_amount / 100) * original_price
        else:
            discount = obj.discount_amount

        final_price = max(original_price - discount, 0)  # ไม่ให้ราคาติดลบ
        return final_price

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "booking", "user", "username", "review_text", "rating", "created_at"]
        read_only_fields = ["id", "user", "username", "created_at"]

class NoShowSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = NoShow
        fields = ["id", "username", "reason", "created_at"]

class HairstyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hairstyle
        fields = ['id', 'name', 'description', 'price',  'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
from rest_framework import serializers

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    
class StylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number']
        
