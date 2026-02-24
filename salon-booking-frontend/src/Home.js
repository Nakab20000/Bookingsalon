import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Header from "./Header";
import "./Home.css";

const Home = () => {
    const [hairstyles, setHairstyles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchHairstyles();
    }, []);

    const fetchHairstyles = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/hairstyles/");
            if (!response.ok) throw new Error("ไม่สามารถโหลดข้อมูลทรงผมได้");

            const data = await response.json();
            setHairstyles(data);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="home-container2">
            <Header />
            <div className="hero-section2">
                <h2 className="main-title2">ระบบจองคิวร้านตัดผม</h2>
                <div className="booking-buttons2">
                    <a href="/booking" className="booking-button2">ตรวจสอบคิวที่ว่างได้เลย</a>
                </div>
            </div>

            <div className="info-section2">
                <h3>ทรงผมแนะนำ</h3>

                {loading ? (
                    <p>⏳ กำลังโหลดข้อมูล...</p>
                ) : error ? (
                    <p style={{ color: "red" }}>❌ {error}</p>
                ) : (
                    <div className="hairstyle-list2">
                        {hairstyles.length > 0 ? (
                            hairstyles.map((style) => (
                                <div key={style.id} className="hairstyle-card2">
                                    <Link to={`/hairstyle/${style.id}`}>
                                        <img
                                            src={style.image || "/images/default-haircut.jpg"}
                                            alt={style.name}
                                            className="hairstyle-image2"
                                        />
                                    </Link>
                                    <h4>{style.name}</h4>
                                </div>
                            ))
                        ) : (
                            <p>❌ ไม่มีทรงผมแนะนำ</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Home;
