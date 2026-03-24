import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './StylistPage.css';
import HeaderAdmin from './HeaderAdmin';

const StylistPage = () => {
    const navigate = useNavigate();
  
    useEffect(() => {
        const role = localStorage.getItem('role');
        if (role !== 'stylist') {
            navigate('/login');
        }
    }, [navigate]);

    return (
        <div className="stylist-page">
            <header>
                <HeaderAdmin />
            </header>

            <div className="content" style={{ display: 'flex', width: '100%' }}>
                <div className="sidebar">
                    <div className="sidebar-header">
                        <h2>Stylist Dashboard</h2>
                    </div>
                    <div className="sidebar-links">
                        <button className="link-item" onClick={() => navigate('/stylist/profile')}> 👤 โปรไฟล์</button>
                        <button className="link-item" onClick={() => navigate('/stylist/portfolio')}> 📂 ผลงาน</button>
                        <button className="link-item" onClick={() => navigate('/stylist/bookings')}>📋 การจองของฉัน</button>
                        <button className="link-item" onClick={() => navigate('/stylist/schedule')}>📅 ตารางเวลา</button>
                        <button className="link-item" onClick={() => navigate('/stylist/reviews')}>⭐ รีวิว</button>
                    </div>
                </div>

                <div className="main-content">
                    <div className="welcome-section">
                        <h1>ยินดีต้อนรับสู่ Stylist Dashboard</h1>
                        <p>สวัสดีค่ะ {localStorage.getItem('first_name') || localStorage.getItem('username')}</p>
                        <p>เลือกเมนูด้านข้าง เพื่อจัดการข้อมูลของคุณ</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StylistPage;
