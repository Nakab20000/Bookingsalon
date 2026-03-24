import React, { useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./SelectDetailsPage.css"

const SelectDetailsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const selectedDate = queryParams.get("date");
    const selectedTime = queryParams.get("time");

    const [bookingDetails, setBookingDetails] = useState({
        hairStyle: "",
        hairType: "",
        promotion: "",
        stylistId: "",
    });

    const [hairstyles, setHairstyles] = useState([]);
    const [promotions, setPromotions] = useState([]);
    const [stylists, setStylists] = useState([]);
    const [finalPrice, setFinalPrice] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        fetchHairstyles();
        fetchPromotions();
        fetchStylists();
    }, []);

    const fetchHairstyles = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/hairstyles/");
            if (!response.ok) throw new Error("ไม่สามารถโหลดทรงผมได้");
            const data = await response.json();
            setHairstyles(data);
        } catch (error) {
            console.error("❌ Error fetching hairstyles:", error);
        }
    };

    const fetchPromotions = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/promotions/");
            if (!response.ok) throw new Error("ไม่สามารถโหลดโปรโมชั่นได้");
            const data = await response.json();
            const today = new Date();
            const validPromotions = data.filter(promo => new Date(promo.end_date) >= today);
            setPromotions(validPromotions);
        } catch (error) {
            console.error("❌ Error fetching promotions:", error);
        }
    };

    const fetchStylists = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/stylists/");
            if (!response.ok) throw new Error("ไม่สามารถโหลดรายชื่อช่างได้");
            const data = await response.json();
            setStylists(data);
        } catch (error) {
            console.error("❌ Error fetching stylists:", error);
        }
    };

    const calculateFinalPrice = useCallback(() => {
        const selectedHairStyle = hairstyles.find(h => h.name === bookingDetails.hairStyle);
        let basePrice = selectedHairStyle ? parseFloat(selectedHairStyle.price) : 0;

        let discount = 0;
        const selectedPromotion = promotions.find(
            promo => String(promo.promotion_id) === String(bookingDetails.promotion)
        );

        if (selectedPromotion) {
            if (selectedPromotion.discount_type === "percent") {
                discount = basePrice * (selectedPromotion.discount_amount / 100);
            } else {
                discount = selectedPromotion.discount_amount;
            }
        }

        setFinalPrice(Math.max(basePrice - discount, 0));
    }, [bookingDetails.hairStyle, bookingDetails.promotion, hairstyles, promotions]);

    useEffect(() => {
        calculateFinalPrice();
    }, [calculateFinalPrice]);

    const handleInputChange = (field, value) => {
        setBookingDetails(prev => ({ ...prev, [field]: value }));
    };

    const handleBookingSubmit = async () => {
        if (!bookingDetails.hairStyle || !bookingDetails.hairType.trim()) {
            alert("กรุณาเลือกทรงผมและกรอกประเภทเส้นผม!");
            return;
        }

        const user_id = localStorage.getItem("user_id");
        const accessToken = localStorage.getItem("accessToken");

        if (!user_id || !accessToken) {
            alert("Session หมดอายุ กรุณาเข้าสู่ระบบอีกครั้ง!");
            navigate("/login");
            return;
        }

        const formattedDate = new Date(selectedDate).toISOString().split("T")[0];

        const bookingData = {
            booking_date: formattedDate,
            booking_time: selectedTime,
            hair_style: bookingDetails.hairStyle,
            hair_type: bookingDetails.hairType,
            promotion: bookingDetails.promotion || null,
            stylist: bookingDetails.stylistId || null,
            price: finalPrice,
        };

        try {
            setIsLoading(true);
            const response = await fetch("http://127.0.0.1:8000/api/create-booking/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify(bookingData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "เกิดข้อผิดพลาดในการจองคิว");
            }

            alert(`จองคิวสำเร็จ! ราคาสุดท้าย: ฿${finalPrice.toFixed(2)} บาท`);
            navigate("/main");
        } catch (error) {
            console.error("Error:", error);
            alert(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="booking12-container">
            <div className="booking12-box">
                <h1 className="booking12-title">เลือกทรงผม</h1>

                <div className="booking12-datetime">
                    <p>📅 วันที่: <strong>{selectedDate}</strong></p>
                    <p>⏰ เวลา: <strong>{selectedTime}</strong></p>
                </div>

                <div className="booking12-field">
                    <label>เลือกทรงผม</label>
                    <select
                        value={bookingDetails.hairStyle}
                        onChange={(e) => handleInputChange("hairStyle", e.target.value)}
                    >
                        <option value="">-- เลือกทรงผม --</option>
                        {hairstyles.map((h) => (
                            <option key={h.id} value={h.name}>
                                {h.name} - ฿{h.price}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="booking12-field">
                    <label>ประเภทเส้นผม</label>
                    <input
                        type="text"
                        placeholder="เช่น ผมตรง / ผมหยักศก"
                        value={bookingDetails.hairType}
                        onChange={(e) => handleInputChange("hairType", e.target.value)}
                    />
                </div>

                <div className="booking12-field">
                    <label>โปรโมชั่น</label>
                    <select
                        value={bookingDetails.promotion}
                        onChange={(e) => handleInputChange("promotion", e.target.value)}
                    >
                        <option value="">ไม่มีโปรโมชั่น</option>
                        {promotions.map((promo) => (
                            <option key={promo.promotion_id} value={promo.promotion_id}>
                                {promo.name} - {promo.discount_amount}
                                {promo.discount_type === "percent" ? "%" : "฿"}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="booking12-field">
                    <label>เลือกช่าง (ถ้ามี)</label>
                    <select
                        value={bookingDetails.stylistId}
                        onChange={(e) => handleInputChange("stylistId", e.target.value)}
                    >
                        <option value="">ไม่ระบุ</option>
                        {stylists.map((stylist) => (
                            <option key={stylist.id} value={stylist.id}>
                                {stylist.first_name} {stylist.last_name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="booking12-price">
                    ราคาสุดท้าย: <span>฿{finalPrice.toFixed(2)}</span>
                </div>

                <button
                    className="booking12-submit"
                    onClick={handleBookingSubmit}
                    disabled={isLoading}
                >
                    {isLoading ? "กำลังบันทึก..." : "ยืนยันการจอง"}
                </button>
            </div>
        </div>

    );


};

export default SelectDetailsPage;
