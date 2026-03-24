import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AdminAddStylistPage.css';
import HeaderAdmin from './HeaderAdmin';

const AdminAddStylistPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password_confirm: '',
        first_name: '',
        last_name: '',
        phone_number: ''
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [stylists, setStylists] = useState([]);

    useEffect(() => {
        const role = localStorage.getItem('role');
        if (role !== 'admin') {
            navigate('/login');
        }
        // ดึงข้อมูล Stylists ที่มีอยู่
        fetchStylists();
    }, [navigate]);

    const fetchStylists = async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const response = await axios.get('http://localhost:8000/api/admin/members/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            // Filter only stylists
            const stylistsOnly = response.data.filter(user => user.role === 'stylist');
            setStylists(stylistsOnly);
        } catch (err) {
            console.error('Error fetching stylists:', err);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        // ตรวจสอบข้อมูล
        if (!formData.username || !formData.email || !formData.password) {
            setError('กรุณากรอกชื่อผู้ใช้ อีเมล และรหัสผ่าน');
            return;
        }

        if (formData.password !== formData.password_confirm) {
            setError('รหัสผ่านไม่ตรงกัน');
            return;
        }

        setLoading(true);
        try {
            const token = localStorage.getItem('accessToken');
            const response = await axios.post(
                'http://localhost:8000/api/admin/create-stylist/',
                {
                    username: formData.username,
                    email: formData.email,
                    password: formData.password,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    phone_number: formData.phone_number
                },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            setMessage(`✅ สร้าง Stylist สำเร็จ: ${formData.first_name} ${formData.last_name}`);
            
            // Reset form
            setFormData({
                username: '',
                email: '',
                password: '',
                password_confirm: '',
                first_name: '',
                last_name: '',
                phone_number: ''
            });

            // อัดเดต stylists list
            fetchStylists();
        } catch (err) {
            const errorMsg = err.response?.data?.error || err.response?.data?.message || 'เกิดข้อผิดพลาด';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="admin-add-stylist-page">
            <header>
                <HeaderAdmin />
            </header>

            <div className="content" style={{ display: 'flex', width: '100%' }}>
                <div className="sidebar">
                    <div className="sidebar-header">
                        <h2>BaBershop Admin</h2>
                    </div>
                    <div className="sidebar-links">
                        <button className="link-item" onClick={() => navigate('/admin')}>📊 Dashboard</button>
                        <button className="link-item" onClick={() => navigate('/admin/create-portfolio')}> 📂 เพิ่มผลงาน</button>
                        <button className="link-item" onClick={() => navigate('/admin/bookings')}>📋 จัดการการจอง</button>
                        <button className="link-item" onClick={() => navigate('/admin/members')}>👥 สมาชิก</button>
                        <button className="link-item" onClick={() => navigate('/admin/add-stylist')}>✂️ เพิ่ม Stylist</button>
                    </div>
                </div>

                <div className="main-content">
                    <div className="container">
                        <h1>➕ เพิ่ม Stylist ใหม่</h1>

                        <div className="form-section">
                            <form onSubmit={handleSubmit} className="add-stylist-form">
                                {error && <div className="error-message">{error}</div>}
                                {message && <div className="success-message">{message}</div>}

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>ชื่อผู้ใช้ *</label>
                                        <input
                                            type="text"
                                            name="username"
                                            value={formData.username}
                                            onChange={handleInputChange}
                                            placeholder="เช่น stylist01"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>อีเมล *</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            placeholder="เช่น stylist@example.com"
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>ชื่อจริง</label>
                                        <input
                                            type="text"
                                            name="first_name"
                                            value={formData.first_name}
                                            onChange={handleInputChange}
                                            placeholder="เช่น สมชาย"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>นามสกุล</label>
                                        <input
                                            type="text"
                                            name="last_name"
                                            value={formData.last_name}
                                            onChange={handleInputChange}
                                            placeholder="เช่น ใจดี"
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>เบอร์โทร</label>
                                        <input
                                            type="tel"
                                            name="phone_number"
                                            value={formData.phone_number}
                                            onChange={handleInputChange}
                                            placeholder="เช่น 0812345678"
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>รหัสผ่าน *</label>
                                        <input
                                            type="password"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleInputChange}
                                            placeholder="ตั้งรหัสผ่าน"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>ยืนยันรหัสผ่าน *</label>
                                        <input
                                            type="password"
                                            name="password_confirm"
                                            value={formData.password_confirm}
                                            onChange={handleInputChange}
                                            placeholder="ยืนยันรหัสผ่าน"
                                            required
                                        />
                                    </div>
                                </div>

                                <button 
                                    type="submit" 
                                    className="submit-btn"
                                    disabled={loading}
                                >
                                    {loading ? '⏳ กำลังสร้าง...' : '✅ สร้าง Stylist'}
                                </button>
                            </form>
                        </div>

                        {/* Stylists List */}
                        <div className="stylists-list-section">
                            <h2>📋 รายชื่อ Stylists ({stylists.length})</h2>
                            {stylists.length > 0 ? (
                                <div className="stylists-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>ชื่อผู้ใช้</th>
                                                <th>ชื่อ-นามสกุล</th>
                                                <th>อีเมล</th>
                                                <th>เบอร์โทร</th>
                                                <th>วันที่เพิ่ม</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {stylists.map(stylist => (
                                                <tr key={stylist.id}>
                                                    <td>{stylist.username}</td>
                                                    <td>{stylist.first_name} {stylist.last_name}</td>
                                                    <td>{stylist.email}</td>
                                                    <td>{stylist.phone_number || '-'}</td>
                                                    <td>{new Date(stylist.date_joined).toLocaleDateString('th-TH')}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p className="no-stylists">ยังไม่มี Stylist</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminAddStylistPage;
