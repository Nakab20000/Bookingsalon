import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminPage.css';
import HeaderAdmin from './HeaderAdmin';

const AdminPage = () => {
    const navigate = useNavigate();
  
    useEffect(() => {
        const role = localStorage.getItem('role');
        if (role !== 'admin') {
            navigate('/login');
        }
    }, [navigate]);

    return (
        <div className="admin-page">
            <header>
                <HeaderAdmin />
            </header>

            <div className="content" style={{ display: 'flex', width: '100%' }}>
                <div className="sidebar">
                    <div className="sidebar-header">
                        <h2>BaBershop</h2>
                    </div>
                    <div className="sidebar-links">
                        <button className="link-item" onClick={() => navigate('/admin/create-portfolio')}> 📂 เพิ่มผลงาน</button>
                        <a href="/admin/portfolio" className="link-item">💇‍♂️ รายละเอียดผลงาน</a>
                        <button className="link-item" onClick={() => navigate('/admin/bookings')}>📋 จัดการการจอง</button>
                        <button className="link-item" onClick={() => navigate('/admin/calendar')}>📅 ดูปฏิทินการจอง</button>
                        <button className="link-item" onClick={() => navigate('/admin/add-promotion')}>🎁 โปรโมชั่น</button>
                        <button className="link-item" onClick={() => navigate('/admin/members')}>👥 สมาชิก</button>
                        <button className="link-item" onClick={() => navigate('/admin/add-stylist')}>✂️ เพิ่ม Stylist</button>
                        <button className="link-item" onClick={() => navigate('/admin/create/hairstyles')}>👥 เพิ่มทรงผม</button>
                        <button className="link-item" onClick={() => navigate('/admin/hairstyles')}>👥 รายละเอียดทรงผม</button>
                    </div>
                </div>

                <div className="main-content">
                    {/* Add more content here if necessary */}
                </div>
            </div>
        </div>
    );
};

export default AdminPage;
