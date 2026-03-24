from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils import timezone

# ✅ Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

# ✅ Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('stylist', 'Stylist'),
        ('guest', 'Guest'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # ✅ เพิ่ม field รูปภาพ
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

# ✅ ตารางจองคิว
from django.db import models
from django.conf import settings
from django.utils import timezone

class Booking(models.Model):
    STATUS_CHOICES = [
        ('จองสำเร็จ', 'จองสำเร็จ'),
        ('ผู้ใช้ยกเลิก', 'ผู้ใช้ยกเลิก'),
        ('แอดมินยกเลิก', 'แอดมินยกเลิก'),
        ('เสร็จสิ้น', 'เสร็จสิ้น'),
        ('รีวิวเสร็จสิ้น', 'รีวิวเสร็จสิ้น'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    hair_style = models.CharField(max_length=255)
    hair_type = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='จองสำเร็จ')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # ✅ เพิ่มราคาการจอง
    promotion = models.ForeignKey("Promotion", on_delete=models.SET_NULL, null=True, blank=True)
    stylist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings_as_stylist')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    cancel_reason = models.TextField(blank=True, null=True) 

    def update_status(self):
        """ อัปเดตสถานะอัตโนมัติเมื่อเลยเวลาจอง """
        now = timezone.localtime(timezone.now())  # เวลาปัจจุบันตามโซนของเซิร์ฟเวอร์
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(self.booking_date, self.booking_time)
        )

        if self.status == 'จองสำเร็จ' and booking_datetime < now:
            self.status = 'จองสำเร็จ'
            self.save()

    def __str__(self):
        stylist_name = self.stylist.username if self.stylist else "No stylist"
        return f"Booking by {self.user.username} on {self.booking_date} at {self.booking_time} with {stylist_name}"
class Promotion(models.Model):
    DISCOUNT_TYPES = [
        ('percent', 'เปอร์เซ็นต์'),
        ('amount', 'บาท'),
    ]

    STATUS_CHOICES = [
        ('created', 'เพิ่มเสร็จแล้ว'),
        ('cancelled', 'ยกเลิกแล้ว'),
    ]

    promotion_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_amount = models.FloatField()
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='amount')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')

    def save(self, *args, **kwargs):
        # ถ้าโปรโมชั่นหมดอายุ ให้เปลี่ยนสถานะเป็น 'cancelled'
        if self.end_date < timezone.now().date():
            self.status = 'cancelled'
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.discount_amount} {self.get_discount_type_display()}) - {self.get_status_display()}"

# ✅ ตารางทรงผม
class Hairstyle(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=120)
    image = models.ImageField(upload_to='hairstyles/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ✅ ตารางรีวิว
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.OneToOneField("Booking", on_delete=models.CASCADE, related_name="review", null=True, blank=True)  # ✅ ชั่วคราวให้ NULL ได้
    rating = models.IntegerField()
    review_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.booking.status = "รีวิวเสร็จสิ้น"  # ✅ อัปเดตสถานะเป็น "รีวิวเสร็จสิ้น"
        self.booking.save()

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} ⭐"

# ✅ ตารางบันทึกคนไม่มาตามคิว
class NoShow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    @staticmethod
    def get_no_show_count(user):
        """ คืนค่าจำนวน No-Show ของผู้ใช้ """
        return NoShow.objects.filter(user=user).count()

    def __str__(self):
        return f"No-Show: {self.user.username} - {self.reason} ({self.get_no_show_count(self.user)} ครั้ง)"


# ✅ ตารางผลงาน (Portfolio)
class Portfolio(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image1 = models.ImageField(upload_to='portfolio_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='portfolio_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='portfolio_images/', null=True, blank=True)
    image4 = models.ImageField(upload_to='portfolio_images/', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title




class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    token = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
