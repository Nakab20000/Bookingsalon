import React, { useState } from 'react';
import authService from './authService';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const StylistLoginPage = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!username || !password) {
            alert("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน!");
            return;
        }

        setLoading(true);

        try {
            const response = await authService.login(username, password);

            if (response.status === 200 && response.data.access && response.data.refresh) {
                // เก็บข้อมูลลง localStorage
                localStorage.setItem("accessToken", response.data.access);
                localStorage.setItem("refreshToken", response.data.refresh);
                localStorage.setItem("username", response.data.username || username);
                localStorage.setItem("user_id", response.data.id);
                localStorage.setItem("role", response.data.role);
                localStorage.setItem("first_name", response.data.first_name || "");
                localStorage.setItem("last_name", response.data.last_name || "");

                // ตรวจสอบว่าเป็น stylist หรือไม่
                if (response.data.role === 'stylist') {
                    navigate('/stylist');
                } else {
                    alert("คุณไม่มีสิทธิ์เข้าสู่ระบบนี้ กรุณาใช้บัญชี Stylist");
                    setLoading(false);
                    return;
                }
            } else {
                alert("เข้าสู่ระบบไม่สำเร็จ กรุณาตรวจสอบข้อมูลอีกครั้ง!");
            }
        } catch (error) {
            console.error("Login failed:", error.response?.data || error.message);
            alert(error.response?.data?.detail || "เข้าสู่ระบบล้มเหลว! กรุณาลองอีกครั้ง.");
        } finally {
            setLoading(false);
        }
    };

    const handleBackToMain = () => {
        navigate('/login');
    };

    const handleResetPassword = () => {
        navigate('/request-reset');
    };

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleSubmit}>
                <div className="stylist-login-header">
                    <h2>✂️ Stylist เข้าสู่ระบบ</h2>
                    <p>สำหรับช่างตัดผม</p>
                </div>

                <div className="form-group">
                    <input
                        type="text"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        placeholder="ชื่อผู้ใช้งาน"
                        required
                    />
                </div>

                <div className="form-group">
                    <input
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="รหัสผ่าน"
                        required
                    />
                </div>

                <button type="submit" className="login-button" disabled={loading}>
                    {loading ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ"}
                </button>

                <div className="login-links">
                    <button type="button" onClick={handleResetPassword} className="link-button">
                        ลืมรหัสผ่าน
                    </button>
                    <button type="button" onClick={handleBackToMain} className="link-button">
                        ← กลับไปหน้าล็อกอินหลัก
                    </button>
                </div>
            </form>
        </div>
    );
};

export default StylistLoginPage;
