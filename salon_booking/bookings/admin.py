from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # กำหนดฟิลด์ที่จะแสดงในหน้า admin list view
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')

    # กำหนดให้สามารถคลิกและแก้ไขได้
    list_editable = ('role',)

    # กำหนดให้ค้นหาได้ด้วยฟิลด์
    search_fields = ('username', 'email')

    # ฟิลด์ที่จะแสดงเมื่อเปิดดูรายละเอียด
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # ฟิลด์ที่ใช้สำหรับเพิ่มผู้ใช้ใหม่
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    
    )
