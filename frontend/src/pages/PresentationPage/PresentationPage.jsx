import React from 'react';
import './PresentationPage.css';
import { useNavigate } from 'react-router-dom';
import PlumLogo from "../../assets/Logo/Logo Pv.png";
import demoFull from '../../assets/demo/ui.png';
import demo1 from '../../assets/demo/demo1.PNG';
import demo2 from '../../assets/demo/Demo2.gif';
import demo3 from '../../assets/demo/Demo3.gif';

const CustomButton = ({ children, variant, link }) => {
    const navigate = useNavigate();

    const handleClick = () => {
        if (link) {
            navigate(link);
        }
    };

    return (
        <button className={variant} onClick={handleClick}>
            {children}
        </button>
    );
};

const features = [
    {
        title: "Instant Analysis",
        desc: "Snap a photo or upload an image of any African plum. Within milliseconds, our AI tells you if it's Unripe, Rotten, Cracked, Spotted, Bruised, or perfectly Healthy. No more guessing get reliable results backed by deep learning.",
        gif: demo1,
        btn: "Try Out",
        link: "/demo",
        reversed: false,
    },
    {
        title: "Live Classification",
        desc: "Turn your camera or webcam into a smart sorting assistant. As plums pass by, our system analyzes each one in real-time, perfect for conveyor belts and small-scale sorting setups.",
        gif: demo2,
        btn: "Go Live",
        link: "/realtime",
        reversed: true,
    },
    {
        title: "Session Statistics",
        desc: "Track everything from class distribution to model confidence of each session. Our dashboard helps you make informed decisions and keep a record of your sorting performance.",
        gif: demo3,
        btn: "View Stats",
        link: "/realtime",
        reversed: false,
    },
];

// Simple component for efficient image loading
const OptimizedImage = ({ src, alt, className }) => {
    return (
        <div className="optimized-image-container">
            <img 
                src={src} 
                alt={alt} 
                className={className}
                loading="lazy" // Native lazy loading
            />
        </div>
    );
};

const PresentationPage = () => {
    return (
        <section className='PresentationPage'>
            <div className="text-block">
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <img src={PlumLogo} alt='Logo PlumVision' style={{ width: '100px', height: '100px' }} />
                </div>
                <h1 className='animated-gradient-text'>PlumVision</h1>
                <p>A smart platform for real-time quality analysis of African plums using computer vision.</p>
            </div>

            <div className='demo-video' data-aos="fade-in">
                <OptimizedImage 
                    src={demoFull} 
                    alt="PlumVision Demo" 
                />
            </div>

            <div className="action-btns">
                <CustomButton variant="filled-black" link="/demo">Demo</CustomButton>
            </div>

            <section className='features-section' id="features">
                {features.map((feature, idx) => (
                    <div key={idx} className={`feature ${feature.reversed ? 'reversed' : ''}`}>
                        <div className="img-box">
                            <OptimizedImage 
                                src={feature.gif} 
                                alt={feature.title}
                                className="feature-image"
                                data-aos="fade-in"
                                data-aos-duration="300"
                            />
                        </div>
                        <div>
                            <h2 className="gradient-text">{feature.title}</h2>
                            <p>{feature.desc}</p>
                            <CustomButton variant="filled-violet" className="feature-button" link={feature.link}>
                                {feature.btn}
                            </CustomButton>
                        </div>
                    </div>
                ))}
            </section>
        </section>
    );
};

export default PresentationPage;