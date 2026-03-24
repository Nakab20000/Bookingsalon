import React, { useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./AdminBookingDetailsPage.css";

const AdminBookingDetailsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const selectedDate = queryParams.get("date");

    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const role = localStorage.getItem("role");
    const title = role === "stylist" ? `📅 รายละเอียดการจองของฉันวันที่ ${selectedDate}` : `📅 รายละเอียดการจองวันที่ ${selectedDate}`;

    // ✅ ใช้ useCallback เพื่อป้องกันปัญหา dependency loop
    const fetchBookings = useCallback(async () => {
        try {
            const accessToken = localStorage.getItem("accessToken");
            const role = localStorage.getItem("role");
            const userId = localStorage.getItem("user_id");

            let apiUrl = `http://127.0.0.1:8000/api/bookings/?date=${selectedDate}`;

            // หากเป็นช่าง ใช้ API ของช่าง (filter ตามวันที่ด้วย)
            if (role === "stylist" && userId) {
                apiUrl = `http://127.0.0.1:8000/api/stylist/${userId}/bookings/?date=${selectedDate}`;
            }

            console.log("📡 Fetching API:", apiUrl);  // ตรวจสอบ URL ที่เรียก API

            const response = await fetch(apiUrl, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
            });

            console.log("📡 API Response Status:", response.status);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to fetch bookings: ${errorText}`);
            }

            const data = await response.json();
            console.log("📡 API Data:", data);  // ตรวจสอบข้อมูลที่ได้รับจาก API

            setBookings(data);
        } catch (error) {
            console.error("❌ Error fetching bookings:", error);
            setError("เกิดข้อผิดพลาดในการโหลดข้อมูล");
        } finally {
            setLoading(false);
        }
    }, [selectedDate]);

    // ✅ ใช้ useEffect เพื่อเรียก fetchBookings เมื่อ selectedDate เปลี่ยน
    useEffect(() => {
        fetchBookings();
    }, [fetchBookings]);

    if (loading) return <p>⏳ กำลังโหลดข้อมูล...</p>;
    if (error) return <p style={{ color: "red" }}>❌ {error}</p>;

    return (
        <div className="booking-details-container">
            <h2>{title}</h2>

            {console.log("📡 แสดงผล bookings:", bookings)} {/* ✅ Debug */}

            {bookings.length > 0 ? (
                <ul>
                    {bookings.map((booking) => {
                        console.log("📡 Booking User:", booking.user);  // ตรวจสอบว่า user มีข้อมูลหรือไม่
                        return (
                            <li key={booking.id}>
                                <p>⏰ เวลา: {booking.booking_time}</p>
                                <p>👤 ผู้จอง: {booking.username}</p> 
                                <p>💇 ทรงผม: {booking.hair_style}</p>
                            </li>
                        );
                    })}

                </ul>

            ) : (
                <p>ไม่มีการจองในวันนี้</p>
            )}

            <button onClick={() => {
                const role = localStorage.getItem("role");
                if (role === "stylist") {
                    navigate("/stylist/schedule");
                } else {
                    navigate("/admin/calendar");
                }
            }}>🔙 กลับไปปฏิทิน</button>
        </div>
    );
};

export default AdminBookingDetailsPage;
