from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from .views import get_members, mark_no_show
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import *

urlpatterns = [
    # User Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('request-reset-password/', RequestPasswordResetView.as_view(), name='request-reset-password'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('verify-reset-token/', VerifyResetTokenView.as_view(), name='verify-reset-token'),
    path('register/', RegisterView.as_view(), name='register'),

    # JWT Authentication Endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # ขอ Access & Refresh Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # ขอ Access Token ใหม่
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # ตรวจสอบความถูกต้องของ Token

    # Portfolio Management
    path('portfolio/create/', PortfolioCreateView.as_view(), name='create-portfolio'),
    path('portfolios/', PortfolioListView.as_view(), name='portfolio-list'),
    path('portfolio/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('portfolio/<int:pk>/edit/', PortfolioUpdateView.as_view(), name='portfolio-edit'),
    path('portfolio/<int:pk>/delete/', PortfolioDeleteView.as_view(), name='portfolio-delete'),
    
    #Member
    path("member-bookings/", MemberBookingsView.as_view(), name="member-bookings"),
    path("user/profile/", UserProfileView.as_view(), name="user-profile"),
    path("member/no-show-count/", NoShowCountView.as_view(), name="no-show-count"),
    path("member/no-show-details/", NoShowDetailsView.as_view(), name="no-show-details"),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    #hairstyles
    path("hairstyles/", HairstyleListView.as_view(), name="hairstyles-list"),
    path("hairstyles/create/", HairstyleListCreateView.as_view(), name="hairstyles-list"),
    path('hairstyles/<int:pk>/', HairstyleDetailsView.as_view(), name='hairstyle-detail'),


    # Booking Management (สำหรับแอดมิน)
    path('bookings/', BookingListView.as_view(), name='booking-list'),  # ดึงข้อมูลการจองทั้งหมด
    path('booking/update-status/<int:booking_id>/', UpdateBookingStatusAPIView.as_view(), name='update-booking-status'),
    path('booking/create/', BookingCreateAPIView.as_view(), name='create-booking'),
    path('booking/<int:pk>/delete/', BookingDeleteAPIView.as_view(), name='delete-booking'),
    path("all-bookings/", get_all_bookings, name="get_all_bookings"),  # ✅ ให้ทุกคนดูข้อมูลคิวทั้งหมด
    path("my-booking-dates/", get_user_booking_dates, name="my-booking-dates"),  # ✅ เพิ่ม API นี้
    path("api/current-time/", CurrentTimeView.as_view(), name="current-time"),

    # Promotions
    path("promotions/", PromotionListView.as_view(), name="promotion-list"),
    path("admin/promotions/", PromotionListCreateView.as_view(), name="promotion-create"),
    path("admin/promotions/<int:promotion_id>/cancel/", cancel_promotion, name="cancel-promotion"),
    path('calculate-price/', calculate_price, name='calculate_price'),

    # Extra Booking API (Frontend)
    path("create-booking/", create_booking, name="create_booking"),

    # Review
    path("review/<int:booking_id>/", submit_review, name="submit_review"),
    path("reviews/", ReviewListView.as_view(), name="reviews"),
    path("my-reviews/", MyReviewsView.as_view(), name="my-reviews"),  # ✅ เพิ่ม API รีวิวของฉัน
    
    #admin
    path("admin/members/", get_members, name="admin-members"),  # ✅ ดึงข้อมูลสมาชิกทั้งหมด
    path("admin/members/<int:user_id>/no-show/", mark_no_show, name="mark-no-show"),  # ✅ บันทึกสถานะ "ไม่มาตามคิว"
    path("admin/no-show/<int:user_id>/", MarkNoShowAPIView.as_view(), name="mark-no-show"),
    path("admin/no-show-members/", NoShowListAPIView.as_view(), name="no-show-list"),
    path("admin/no-show-count/", NoShowCountView.as_view(), name="no-show-list"),


]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
