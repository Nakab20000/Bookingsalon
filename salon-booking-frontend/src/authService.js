import axios from 'axios';

const API_URL = "http://localhost:8000/api/";

// ✅ ฟังก์ชัน register สำหรับลงทะเบียน
const register = (username, email, password, passwordConfirmation, phoneNumber, firstName, lastName, role = 'member') => {
    return axios.post(API_URL + "register/", {
        username,
        email,
        password,
        password_confirmation: passwordConfirmation,
        phone_number: phoneNumber,
        first_name: firstName,
        last_name: lastName,
        role,
    });
};

// ✅ ฟังก์ชัน login สำหรับเข้าสู่ระบบ (เก็บ Token ใน localStorage)
const login = async (username, password) => {
    try {
        const response = await axios.post(API_URL + "login/", { username, password });

        if (response.status === 200) {
            localStorage.setItem("accessToken", response.data.access);
            localStorage.setItem("refreshToken", response.data.refresh);
            localStorage.setItem("role", response.data.role);
            return response;
        } else {
            throw new Error("Invalid response status");
        }
    } catch (error) {
        console.error("Login error:", error.response?.data || error.message);
        throw error;
    }
};

// ✅ ฟังก์ชัน logout (เคลียร์ Token และส่ง `POST` ไปที่ API)
const logout = () => {
    const refreshToken = localStorage.getItem("refreshToken");
    return axios.post(API_URL + "logout/", { refresh: refreshToken });
};

// ✅ ฟังก์ชัน resetPassword (ส่ง Token และข้อมูล)
const resetPassword = (oldPassword, newPassword) => {
    const accessToken = localStorage.getItem("accessToken");
    return axios.post(
        API_URL + "reset-password/",
        { old_password: oldPassword, new_password: newPassword },
        {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        }
    );
};

// ✅ ฟังก์ชัน getUserProfile (ต้องส่ง Token)
const getUserProfile = () => {
    const accessToken = localStorage.getItem("accessToken");
    return axios.get("http://127.0.0.1:8000/api/user/profile/", {
        headers: { Authorization: `Bearer ${accessToken}` },
    });
};

// ✅ ฟังก์ชัน updateUserProfile (ต้องส่ง Token)
const updateUserProfile = (updatedData) => {
    const accessToken = localStorage.getItem("accessToken");
    return axios.put("http://127.0.0.1:8000/api/user/profile/", updatedData, {
        headers: { Authorization: `Bearer ${accessToken}` },
    });
};

// ✅ ฟังก์ชัน createPortfolio (ต้องส่ง Token และใช้ `multipart/form-data`)
const createPortfolio = (formData) => {
    const accessToken = localStorage.getItem("accessToken");
    return axios.post(API_URL + "portfolio/create/", formData, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'multipart/form-data'
        }
    });
};

// ✅ ฟังก์ชัน getPortfolios
const getPortfolios = () => {
    return axios.get(`${API_URL}portfolios/`);
};

// ✅ ฟังก์ชัน getPortfolio
const getPortfolio = (id) => {
    return axios.get(`${API_URL}portfolios/${id}/`);
};

// ✅ ฟังก์ชัน updatePortfolio (ต้องส่ง Token และใช้ `multipart/form-data`)
const updatePortfolio = (id, data) => {
    const accessToken = localStorage.getItem("accessToken");

    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('description', data.description);
    if (data.image1) formData.append('image1', data.image1);
    if (data.image2) formData.append('image2', data.image2);
    if (data.image3) formData.append('image3', data.image3);
    if (data.image4) formData.append('image4', data.image4);

    return axios.put(`${API_URL}portfolio/${id}/edit/`, formData, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'multipart/form-data',
        },
    });
};

// ✅ ฟังก์ชัน deletePortfolio
const deletePortfolio = (id) => {
    const accessToken = localStorage.getItem("accessToken");
    return axios.delete(`${API_URL}portfolio/${id}/delete/`, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
};

// ✅ ฟังก์ชัน createBooking (ต้องส่ง Token)
const createBooking = async (data) => {
    const accessToken = localStorage.getItem("accessToken");

    try {
        const response = await axios.post(`${API_URL}booking/create/`, data, {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });

        console.log(response.data);
        alert("จองคิวสำเร็จ!");
    } catch (error) {
        console.error(error.response?.data || error.message);
        alert("เกิดข้อผิดพลาดในการจองคิว");
    }
};

// ✅ ฟังก์ชัน cancelBooking (ต้องใช้ `PUT` และส่ง Token)
const cancelBooking = async (bookingId, status) => {
    const accessToken = localStorage.getItem("accessToken");

    try {
        const response = await axios.put(
            `${API_URL}booking/update-status/${bookingId}/`,
            { status },
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            }
        );

        alert("สถานะถูกอัปเดตเรียบร้อยแล้ว!");
        console.log(response.data);
    } catch (error) {
        console.error(error.response?.data || error.message);
        alert("เกิดข้อผิดพลาดในการอัปเดตสถานะ");
    }
};

// ✅ ส่งออกฟังก์ชันทั้งหมด
const authService = {
    register,
    login,
    logout,
    resetPassword,
    getUserProfile,
    updateUserProfile,
    createPortfolio,
    getPortfolios,
    getPortfolio,
    updatePortfolio,
    deletePortfolio,
    createBooking,
    cancelBooking,
};

export default authService;
