from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from rest_framework.authentication import TokenAuthentication
from .models import PasswordResetToken  # โมเดลสำหรับเก็บโค้ดรีเซ็ต
from .serializers import PasswordResetRequestSerializer, ResetPasswordSerializer
import random
import string
from django.core.mail import send_mail
from .models import Booking, Hairstyle, Portfolio, Promotion , Review
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Booking
from .models import *
from .serializers import *
from .serializers import BookingSerializer

from .serializers import (
    ReviewSerializer,
    BookingSerializer,
    PortfolioSerializer,
    PromotionSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)

User = get_user_model()

# ------------------- 🔹 AUTHENTICATION & USER MANAGEMENT -------------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            # ใช้ role ที่เก็บใน CustomUser (หรือ 'admin' หากเป็น superuser)
            user_role = 'admin' if user.is_superuser else getattr(user, 'role', 'member')

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user_role,
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
class VerifyResetTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token is required"}, status=400)

        # ตรวจสอบว่า token นี้มีอยู่ในฐานข้อมูลหรือไม่
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            return Response({"is_valid": True}, status=200)
        except PasswordResetToken.DoesNotExist:
            return Response({"is_valid": False}, status=404)
        
class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["new_password"]
            
            # ดำเนินการตามที่ต้องการ เช่น ตรวจสอบ token และทำการรีเซ็ตรหัสผ่าน
            reset_entry = PasswordResetToken.objects.filter(user__email=email, token=token).first()
            if reset_entry:
                user = reset_entry.user
                user.set_password(new_password)
                user.save()
                reset_entry.delete()  # ลบ token ออกหลังจากใช้แล้ว
                return Response({"message": "Password has been reset"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                # สร้างโค้ดรีเซ็ต
                reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                PasswordResetToken.objects.create(user=user, token=reset_code)

                # ส่งอีเมล
                send_mail(
                    "Password Reset Code",
                    f"Your reset code is: {reset_code}",
                    "no-reply@yourdomain.com",
                    [email],
                    fail_silently=False,
                )

                # ส่งข้อความและโค้ดคืนไปใน response
                return Response({
                    "message": "Reset code sent to your email",
                    "token": reset_code  # ส่ง token กลับไปด้วย
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ ต้องล็อกอินก่อนเข้าถึงข้อมูล
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request):
        """ดึงข้อมูลโปรไฟล์ของผู้ใช้ที่ล็อกอินอยู่"""
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=200)

    def put(self, request):
        """อัปเดตข้อมูลโปรไฟล์ของผู้ใช้"""
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        

        return Response(serializer.errors, status=400)

class CreateAdminUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_superuser(username=username, email=email, password=password)
        return Response({"message": "Admin user created successfully."}, status=status.HTTP_201_CREATED)

class CreateStylistView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")

        if not username or not email or not password:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role='stylist'
        )

        return Response({"message": "Stylist created successfully."}, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
# ------------------- 🔹 BOOKINGS -------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_member_bookings(request):
    user = request.user

    # หากเป็น Stylist ให้แสดงเฉพาะการจองที่มอบหมายให้ตนเอง
    if getattr(user, "role", None) == "stylist":
        bookings = Booking.objects.filter(stylist=user).order_by("-booking_date")
    else:
        # กรณีสมาชิกทั่วไป ให้แสดงเฉพาะการจองของตนเอง
        bookings = Booking.objects.filter(user=user).order_by("-booking_date")

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

class MemberBookingsView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ ต้องล็อกอินก่อนเข้าถึง

    def get(self, request):
        user = request.user  # ✅ ดึงข้อมูลผู้ใช้ที่ล็อกอิน
        bookings = Booking.objects.filter(user=user).order_by("-booking_date")
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=200)
    
@api_view(["GET"])
@permission_classes([IsAdminUser])  # ✅ ให้เฉพาะแอดมินดูได้
def get_all_bookings(request):
    bookings = Booking.objects.all().values(
        "id", "booking_date", "booking_time", "user__username", 
        "hair_style", "status", "cancel_reason"  # ✅ เพิ่มเหตุผลยกเลิก
    )

    data = [
        {
            "booking_id": b["id"],
            "booking_date": b["booking_date"].strftime("%Y-%m-%d"),  # 📅 `YYYY-MM-DD`
            "booking_time": b["booking_time"].strftime("%H:%M"),  # ⏰ `HH:MM`
            "user": {"username": b["user__username"]},  # 👤 ใครจอง
            "hair_style": b["hair_style"],
            "status": b["status"],
            "cancel_reason": b["cancel_reason"] if b["cancel_reason"] else "-"  # ✅ ถ้าไม่มีเหตุผลให้แสดง "-"
        }
        for b in bookings
    ]
    return JsonResponse(data, safe=False)

@api_view(["GET"])
def get_bookings(request):
    date = request.GET.get("date")
    print(f"API called with date: {date}")  # แสดงวันที่จาก Query Param
    if not date:
        return JsonResponse({"error": "กรุณาระบุวันที่ใน Query Parameter"}, status=400)

    bookings = Booking.objects.filter(booking_date=date)
    print(f"Bookings found: {bookings}")  # แสดงรายการที่พบใน Log

    data = [{"booking_time": b.booking_time} for b in bookings]
    return JsonResponse(data, safe=False)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_booking_dates(request):
    """
    API ดึงวันที่ที่ผู้ใช้มีการจองอยู่ (ยกเว้นที่ถูกยกเลิก)
    """
    user = request.user  # ✅ ดึงข้อมูลผู้ใช้จาก Token
    excluded_statuses = ["ผู้ใช้ยกเลิก", "แอดมินยกเลิก"]  # ✅ ไม่เอาสถานะที่ถูกยกเลิก
    bookings = Booking.objects.filter(user=user).exclude(status__in=excluded_statuses).values_list("booking_date", flat=True)

    booking_dates = list(set(bookings))  # ✅ เอาเฉพาะวันที่ไม่ซ้ำกัน

    return Response({"booking_dates": booking_dates})


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        date = self.request.query_params.get("date")
        now = timezone.localtime(timezone.now()).date()  # ✅ เวลาปัจจุบัน (เอาเฉพาะวันที่)
        
        # ✅ เอาเฉพาะคิวที่ไม่ถูกยกเลิก และไม่เลยวันปัจจุบัน
        queryset = Booking.objects.exclude(status__in=["ผู้ใช้ยกเลิก", "แอดมินยกเลิก"]).filter(booking_date__gte=now)

        # ✅ อัปเดตสถานะของการจองที่เลยเวลาไปแล้ว
        for booking in queryset:
            booking.update_status()

        if date:
            queryset = queryset.filter(booking_date=date)

        return queryset
from rest_framework import generics, views

# ✅ API ดึงเวลาปัจจุบันจากเซิร์ฟเวอร์
class CurrentTimeView(views.APIView):
    def get(self, request):
        current_time = timezone.localtime(timezone.now()).strftime("%H:%M")
        return Response({"current_time": current_time})
    
class BookingCreateAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print("Data being saved:", serializer.validated_data)
        serializer.save()


class UpdateBookingStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, booking_id=None):
        print(f"📌 Received booking_id: {booking_id}")

        if not booking_id:
            return Response({"error": "ไม่พบ ID ของการจอง กรุณาลองใหม่!"}, status=400)

        booking = get_object_or_404(Booking, id=booking_id)
        new_status = request.data.get("status")
        reason = request.data.get("reason", "")  # ✅ เพิ่มเหตุผลการยกเลิก

        if new_status not in ["จองสำเร็จ", "ผู้ใช้ยกเลิก", "แอดมินยกเลิก", "เสร็จสิ้น"]:
            return Response({"error": "สถานะไม่ถูกต้อง"}, status=400)

        booking.status = new_status
        if new_status in ["ผู้ใช้ยกเลิก", "แอดมินยกเลิก"]:
            booking.cancel_reason = reason  # ✅ บันทึกเหตุผลการยกเลิก
        booking.save()

        return Response({"message": f"อัปเดตสถานะเป็น {new_status} สำเร็จ!"})


class BookingDeleteAPIView(generics.DestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_booking(request):
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({"message": "จองคิวสำเร็จ!", "data": serializer.data}, status=201)
    return Response(serializer.errors, status=400)


# ------------------- 🔹 PORTFOLIO -------------------

@api_view(['POST'])
def create_portfolio(request):
    if request.method == 'POST':
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfolioCreateView(APIView):
    def post(self, request):
        # รับไฟล์ที่ส่งมาใน request.FILES
        serializer = PortfolioSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PortfolioListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        portfolios = Portfolio.objects.all()
        serializer = PortfolioSerializer(portfolios, many=True, context={'request': request})
        return Response(serializer.data)
    
class PortfolioUpdateView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, id):
        portfolio = get_object_or_404(Portfolio, id=id)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfolioDeleteView(generics.DestroyAPIView):
    queryset = Portfolio.objects.all()

class PortfolioDetailView(APIView):
    permission_classes = [AllowAny]  # ใช้สิทธิ์การเข้าถึงที่ต้องการ

    def get(self, request, pk):
        try:
            portfolio = Portfolio.objects.get(id=pk)
        except Portfolio.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)


# ------------------- 🔹 PROMOTIONS -------------------

class PromotionListView(generics.ListAPIView):
    queryset = Promotion.objects.filter(is_active=True)
    serializer_class = PromotionSerializer
    permission_classes = [AllowAny]

class PromotionListCreateView(APIView):
    permission_classes = [IsAdminUser]  # ✅ ให้เฉพาะแอดมินใช้ API นี้

    def get(self, request):
        # อัปเดตสถานะโปรโมชั่นที่หมดอายุ
        promotions = Promotion.objects.all()
        for promo in promotions:
            if promo.end_date < timezone.now().date() and promo.status != 'cancelled':
                promo.status = 'cancelled'
                promo.is_active = False
                promo.save()

        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def cancel_promotion(request, promotion_id):
    promotion = get_object_or_404(Promotion, promotion_id=promotion_id)
    if not promotion.is_active:
        return Response({"message": "โปรโมชั่นนี้ถูกยกเลิกไปแล้ว"}, status=400)

    promotion.is_active = False
    promotion.save()
    return Response({"message": "✅ โปรโมชั่นถูกยกเลิกเรียบร้อยแล้ว"})

@api_view(['POST'])
def calculate_price(request):
    hairstyle_id = request.data.get('hairstyle_id')
    promotion_id = request.data.get('promotion_id')

    hairstyle = get_object_or_404(Hairstyle, id=hairstyle_id)
    base_price = hairstyle.price
    final_price = base_price

    if promotion_id:
        promotion = get_object_or_404(Promotion, promotion_id=promotion_id)
        if promotion.discount_type == 'percent':
            discount = base_price * (promotion.discount_amount / 100)
        else:
            discount = promotion.discount_amount
        final_price = max(base_price - discount, 0)

    return Response({'final_price': final_price}, status=status.HTTP_200_OK)

# ------------------- 🔹 รีวิว -------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_review(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user, status="เสร็จสิ้น")
        if hasattr(booking, "review"):  # ✅ เช็คว่ามีรีวิวอยู่แล้วหรือไม่
            return Response({"error": "คุณได้รีวิวไปแล้ว!"}, status=400)

        rating = request.data.get("rating")
        review_text = request.data.get("review_text")

        if not rating or not review_text:
            return Response({"error": "กรุณากรอกคะแนนและรีวิว"}, status=400)

        review = Review.objects.create(
            booking=booking,
            user=request.user,
            rating=rating,
            review_text=review_text
        )

        booking.status = "รีวิวเสร็จสิ้น"  # ✅ อัปเดตสถานะ
        booking.save()

        return Response({"message": "รีวิวสำเร็จ!"})
    except Booking.DoesNotExist:
        return Response({"error": "ไม่พบการจอง หรือคุณยังไม่สามารถรีวิวได้"}, status=404)

class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # ✅ ทุกคนดูรีวิวได้ (ผู้ใช้ทั่วไป, สมาชิก, แอดมิน)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and self.request.query_params.get("my_reviews"):
            return Review.objects.filter(user=user)  # ✅ คืนค่ารีวิวของผู้ใช้ที่ล็อกอิน
        return Review.objects.all()  # ✅ คืนค่าทุกรีวิวถ้าไม่ส่ง `my_reviews`
    
class MyReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
## คนไม่มาตามคิว
@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_members(request):
    members = User.objects.values(
        "id", "username", "email", "phone_number", "first_name", "last_name"
    )
    return Response(members)

@api_view(["PUT"])
@permission_classes([IsAdminUser])
def mark_no_show(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.status = "ไม่มาตามคิว"
        user.no_show_reason = request.data.get("reason", "")
        user.save()
        return Response({"message": "บันทึกสถานะเรียบร้อยแล้ว"})
    except User.DoesNotExist:
        return Response({"error": "ไม่พบผู้ใช้"}, status=404)
    
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import NoShow
from .serializers import NoShowSerializer

# ✅ API สำหรับเพิ่มคนไม่มาตามคิว
class MarkNoShowAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        reason = request.data.get("reason", "")
        if not reason:
            return Response({"error": "กรุณากรอกเหตุผล"}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "ไม่พบผู้ใช้"}, status=404)

        # สร้างบันทึก No-Show
        NoShow.objects.create(user=user, reason=reason)
        return Response({"message": f"บันทึก No-Show ของ {user.username} สำเร็จ!"}, status=201)


# ✅ API สำหรับดูรายการ No-Show
class NoShowListAPIView(generics.ListAPIView):
    queryset = NoShow.objects.all()
    serializer_class = NoShowSerializer
    permission_classes = [permissions.IsAdminUser]

# ✅ API สำหรับดึงจำนวนครั้งที่ผู้ใช้ไม่มาตามคิว
from django.db.models import Count  # เพิ่มบรรทัดนี้
class NoShowCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ดึงข้อมูลผู้ใช้ที่ล็อกอิน
        user = request.user
        
        # นับจำนวน No-Show สำหรับผู้ใช้
        no_show_counts = NoShow.objects.filter(user=user).values('user').annotate(count=Count('id'))

        # สร้าง dictionary ที่มี user.id เป็น key และ count เป็น value
        count_data = {str(count['user']): count['count'] for count in no_show_counts}

        # ส่งข้อมูลกลับไป
        return Response(count_data)
    
# ✅ API สำหรับดึงรายละเอียดของการไม่มาตามคิว
class NoShowDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        no_show_records = NoShow.objects.filter(user=user).order_by("-created_at").values("reason", "created_at")
        return Response(list(no_show_records))

from .serializers import HairstyleSerializer
## ทรงผม

class HairstyleListCreateView(generics.ListCreateAPIView):
    queryset = Hairstyle.objects.all()
    serializer_class = HairstyleSerializer
    permission_classes = [IsAdminUser]  # ให้เฉพาะแอดมินเพิ่มได้
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

class HairstyleListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  
    queryset = Hairstyle.objects.all()
    serializer_class = HairstyleSerializer

class HairstyleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hairstyle.objects.all()
    serializer_class = HairstyleSerializer
    permission_classes = [IsAdminUser]  # ✅ ให้เฉพาะแอดมินเข้าถึง
    
class HairstyleDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hairstyle.objects.all()
    serializer_class = HairstyleSerializer
    permission_classes = [AllowAny]  # ✅ ให้เฉพาะแอดมินเข้าถึง


class StylistListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(role='stylist')
    serializer_class = StylistSerializer
    permission_classes = [AllowAny]

class StylistBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, stylist_id):
        date = request.query_params.get("date")
        bookings = Booking.objects.filter(stylist_id=stylist_id).order_by("-booking_date")

        if date:
            bookings = bookings.filter(booking_date=date)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=200)
     
    