import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "./MemberBookingsPage.css";

const StylistBookingsPage = () => {
    const navigate = useNavigate();
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [cancelReasons, setCancelReasons] = useState({});
    const [activeTab, setActiveTab] = useState("bookings");

    const fetchStylistBookings = useCallback(async () => {
        try {
            const accessToken = localStorage.getItem("accessToken");
            const stylistId = localStorage.getItem("user_id");

            if (!accessToken || !stylistId) {
                alert("Session หมดอายุ กรุณาเข้าสู่ระบบอีกครั้ง!");
                navigate("/login");
                return;
            }

            const response = await fetch(`http://127.0.0.1:8000/api/stylist/${stylistId}/bookings/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            if (!response.ok) {
                throw new Error("ไม่สามารถโหลดข้อมูลการจองของช่างได้");
            }

            const data = await response.json();
            setBookings(data);
        } catch (error) {
            setError("เกิดข้อผิดพลาดในการโหลดข้อมูล");
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    useEffect(() => {
        fetchStylistBookings();
    }, [fetchStylistBookings]);

    const handleRequestCancel = (bookingId) => {
        setCancelReasons((prev) => ({ ...prev, [bookingId]: "" }));
    };

    const handleCancelRequest = (bookingId) => {
        setCancelReasons((prev) => {
            const updated = { ...prev };
            delete updated[bookingId];
            return updated;
        });
    };

    const handleConfirmCancel = async (bookingId) => {
        const reason = cancelReasons[bookingId] || "";
        if (!reason) {
            alert("⚠ กรุณากรอกเหตุผลในการยกเลิก");
            return;
        }

        try {
            const accessToken = localStorage.getItem("accessToken");
            const response = await fetch(`http://127.0.0.1:8000/api/booking/update-status/${bookingId}/`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify({ status: "แอดมินยกเลิก", reason }),
            });

            if (!response.ok) {
                throw new Error("Failed to cancel booking.");
            }

            alert("✅ ยกเลิกการจองสำเร็จ!");
            fetchStylistBookings();
        } catch (error) {
            alert("❌ เกิดข้อผิดพลาด: " + error.message);
        }
    };

    if (loading) return <p>⏳ กำลังโหลดข้อมูล...</p>;
    if (error) return <p style={{ color: "red" }}>❌ {error}</p>;

    const upcomingBookings = bookings.filter((booking) => booking.status !== "เสร็จสิ้น");
    const completedBookings = bookings.filter((booking) => booking.status === "เสร็จสิ้น");

    return (
        <div className="member-page">
            <h2>📅 คิวของฉัน (Stylist)</h2>

            <div className="tabs">
                <button
                    className={activeTab === "bookings" ? "active-tab" : ""}
                    onClick={() => setActiveTab("bookings")}
                >
                    📋 คิวของฉัน
                </button>
                <button
                    className={activeTab === "reviews" ? "active-tab" : ""}
                    onClick={() => setActiveTab("reviews")}
                >
                    ⭐ รีวิวของฉัน
                </button>
            </div>

            {activeTab === "bookings" && (
                <table className="booking-table">
                    <thead>
                        <tr>
                            <th>วันที่</th>
                            <th>เวลา</th>
                            <th>ทรงผม</th>
                            <th>ราคา (บาท)</th>
                            <th>สถานะ</th>
                            <th>เหตุผลยกเลิก</th>
                            <th>จัดการ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {upcomingBookings.map((booking) => (
                            <tr key={booking.id}>
                                <td>{booking.booking_date}</td>
                                <td>{booking.booking_time}</td>
                                <td>{booking.hair_style}</td>
                                <td>{booking.price} ฿</td>
                                <td className={`status-${booking.status}`}>{booking.status}</td>
                                <td>{booking.cancel_reason || "-"}</td>
                                <td>
                                    {booking.status === "จองสำเร็จ" && (
                                        cancelReasons[booking.id] === undefined ? (
                                            <button className="cancel-btn" onClick={() => handleRequestCancel(booking.id)}>
                                                ❌ ยกเลิก
                                            </button>
                                        ) : (
                                            <>
                                                <input
                                                    type="text"
                                                    placeholder="กรอกเหตุผล..."
                                                    value={cancelReasons[booking.id]}
                                                    onChange={(e) =>
                                                        setCancelReasons({
                                                            ...cancelReasons,
                                                            [booking.id]: e.target.value,
                                                        })
                                                    }
                                                />
                                                <button className="confirm-btn" onClick={() => handleConfirmCancel(booking.id)}>
                                                    ✅ ยืนยัน
                                                </button>
                                                <button className="cancel-btn" onClick={() => handleCancelRequest(booking.id)}>
                                                    ❌ ยกเลิก
                                                </button>
                                            </>
                                        )
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}

            {activeTab === "reviews" && (
                <table className="booking-table">
                    <thead>
                        <tr>
                            <th>วันที่</th>
                            <th>เวลา</th>
                            <th>ทรงผม</th>
                            <th>สถานะ</th>
                            <th>รีวิว</th>
                        </tr>
                    </thead>
                    <tbody>
                        {completedBookings.map((booking) => (
                            <tr key={booking.id}>
                                <td>{booking.booking_date}</td>
                                <td>{booking.booking_time}</td>
                                <td>{booking.hair_style}</td>
                                <td className={`status-${booking.status}`}>{booking.status}</td>
                                <td>
                                    {booking.review ? (
                                        <div>
                                            <p>⭐ {booking.review.rating} ดาว</p>
                                            <p>{booking.review.review_text}</p>
                                        </div>
                                    ) : (
                                        <button
                                            className="review-btn"
                                            onClick={() => navigate(`/review/${booking.id}`)}
                                        >
                                            ✍ รีวิว
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default StylistBookingsPage;
