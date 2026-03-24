import React, { useState } from 'react';
import authService from './authService';
import { useNavigate } from 'react-router-dom';
import './Register.css';

const Register = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [passwordConfirmation, setPasswordConfirmation] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const navigate = useNavigate();
    const role = "member";

    const handleSubmit = (e) => {
        e.preventDefault();
        authService.register(username, email, password, passwordConfirmation, phoneNumber, firstName, lastName, role)
            .then(response => {
                console.log(response.data);
                if (response.status === 201) {
                    navigate('/login');
                } else {
                    alert("Registration was not successful. Please try again.");
                }
            })
            .catch(error => {
                console.error("Registration failed:", error);
                if (error.response && error.response.data) {
                    const errors = error.response.data;
                    let errorMessage = "Registration failed:\n";
                    for (let key in errors) {
                        errorMessage += `${key}: ${errors[key]}\n`;
                    }
                    alert(errorMessage);
                } else {
                    alert("Registration failed. Please try again.");
                }
            });
    };

    return (
        <div className="register-container">
            <form className="register-form" onSubmit={handleSubmit}>
                <h2 className="register-title">สมัครสมาชิก</h2>
                <div className="form-group">
                    <input 
                        type="text" 
                        value={username} 
                        onChange={e => setUsername(e.target.value)} 
                        placeholder="ชื่อผู้ใช้งาน" 
                    />
                </div>
                <div className="form-group">
                    <input 
                        type="password" 
                        value={password} 
                        onChange={e => setPassword(e.target.value)} 
                        placeholder="รหัสผ่าน" 
                    />
                </div>
                <div className="form-group">
                    <input 
                        type="password" 
                        value={passwordConfirmation} 
                        onChange={e => setPasswordConfirmation(e.target.value)} 
                        placeholder="ยืนยันรหัสผ่าน" 
                    />
                </div>
                <div className="form-group form-column">
                    <div className="form-column">
                        <input 
                            type="text" 
                            value={firstName} 
                            onChange={e => setFirstName(e.target.value)} 
                            placeholder="ชื่อจริง" 
                        />
                        <input 
                            type="text" 
                            value={lastName} 
                            onChange={e => setLastName(e.target.value)} 
                            placeholder="นามสกุล" 
                        />
                    </div>
                </div>
                <div className="form-group">
                    <input 
                        type="email" 
                        value={email} 
                        onChange={e => setEmail(e.target.value)} 
                        placeholder="อีเมล" 
                    />
                </div>
                <div className="form-group">
                    <input 
                        type="text" 
                        value={phoneNumber} 
                        onChange={e => setPhoneNumber(e.target.value)} 
                        placeholder="เบอร์โทร" 
                    />
                </div>
                <button type="submit" className="register-button">บันทึก</button>
            </form>
        </div>
    );
};

export default Register;
