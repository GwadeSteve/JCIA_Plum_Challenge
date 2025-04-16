import React from 'react';
import './PresentationPage.css';
import { useNavigate } from 'react-router-dom';
import demofull from '../../assets/demo/full_demo.gif';

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
        title: "Instant Plum Analysis",
        desc: "Snap a photo or upload an image of any African plum. Within milliseconds, our AI tells you if it's Unripe, Rotten, Cracked, Spotted, Bruised, or perfectly Healthy. No more guessing—get fast, reliable results backed by deep learning.",
        gif: "/feature1.gif",
        btn: "Try It Now",
        link: "/demo",
        reversed: false,
    },
    {
        title: "Live Camera Classification",
        desc: "Turn your camera into a smart sorting assistant. As plums pass by, our system analyzes each one in real-time, perfect for conveyor belts and small-scale sorting setups. It's automation made accessible.",
        gif: "/feature2.gif",
        btn: "Start Live Stream",
        link: "/realtime",
        reversed: true,
    },
    {
        title: "Session Analytics",
        desc: "Track everything. From class distribution and model confidence to auto-generated summaries of each session. Our dashboard helps you make informed decisions and keep a record of your sorting performance.",
        gif: "/feature3.gif",
        btn: "View Insights",
        link: "/stats",
        reversed: false,
    },
];

const PresentationPage = () => {
    return (
        <section className='PresentationPage'>
            <div className="text-block">
                <div  style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <img src="./Logo Pv.png" alt='Logo PlumVision' style={{ width: '200px', height: '200px' }} />
                </div>
                <h1 className='animated-gradient-text'>PlumVision</h1>
                <p>A smart platform for real-time quality analysis of African plums using computer vision.</p>
            </div>

            <div className='demo-video' data-aos="fade-in">
                <img src={demofull} alt="PlumVision Demo" />
            </div>

            <div className="action-btns">
                <CustomButton variant="filled-black" link="/demo">Try Demo</CustomButton>
            </div>

            <section className='features-section' id="features">
                {features.map((feature, idx) => (
                    <div key={idx} className={`feature ${feature.reversed ? 'reversed' : ''}`}>
                        <img data-aos="fade-in" data-aos-duration="300" src={feature.gif} alt={feature.title} />
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