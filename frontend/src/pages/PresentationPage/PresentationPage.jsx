import React, { lazy, Suspense } from 'react';
import './PresentationPage.css';
import { useNavigate } from 'react-router-dom';
import PlumLogo from "../../assets/Logo/Logo Pv.png";
import demoFull from '../../assets/demo/full_demo.gif';
import demo1 from '../../assets/demo/Demo1.gif';
import demo2 from '../../assets/demo/Demo2.gif';
import demo3 from '../../assets/demo/Demo3.gif';
import farmerImage from "../../assets/team/Farmer.png"
import { BsLightningCharge } from 'react-icons/bs';
import { MdOutlineSignalWifiOff, MdOutlinePhoneAndroid, MdOutlineAccessTime } from 'react-icons/md';

const LazyImage = lazy(() => import('../../components/LazyImage/LazyImage'));
const placeholder = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";

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
                <Suspense fallback={<div className="placeholder-loading"></div>}>
                    <LazyImage 
                        src={demoFull} 
                        placeholder={placeholder} 
                        alt="PlumVision Demo" 
                    />
                </Suspense>
            </div>

            <div className="action-btns">
                <CustomButton variant="filled-black" link="/demo">Demo</CustomButton>
            </div>

            <section className="community-impact">
                     
                    <div className="impact-visual-section">
                      <div className="impact-visual-content">
                        <h3 className="l-font">Technology That Makes Sense Here</h3>
                        <p className="m-font">
                          Understanding farmers and enterprises challenges before writing a single line of code was key. Our solution is not only technically sound, it's relevant and useful for the people who need it most.
                        </p>
                        <div className="impact-features">
                          <div className="impact-feature" data-aos="fade-left" data-aos-duration="300">
                            <div className="feature-icon">
                              <MdOutlineSignalWifiOff />
                            </div>
                            <div className="feature-text">
                              <h4>Available Offline</h4>
                              <p>PlumVision can function without internet access</p>
                            </div>
                          </div>
                          <div className="impact-feature" data-aos="fade-left" data-aos-duration="350">
                            <div className="feature-icon">
                              <BsLightningCharge />
                            </div>
                            <div className="feature-text">
                              <h4>Real-time Analysis</h4>
                              <p>Obtain results in seconds, and keep pace with busy days</p>
                            </div>
                          </div>
                          <div className="impact-feature" data-aos="fade-left" data-aos-duration="400">
                            <div className="feature-icon">
                              <MdOutlinePhoneAndroid />
                            </div>
                            <div className="feature-text">
                              <h4>Performance Beast</h4>
                              <p>Optimized for the devices farmers already own</p>
                            </div>
                          </div>
                          <div className="impact-feature" data-aos="fade-left" data-aos-duration="450">
                            <div className="feature-icon">
                              <MdOutlineAccessTime />
                            </div>
                            <div className="feature-text">
                              <h4>Learns Over Time</h4>
                              <p>Our model improves over time, adapting to changing conditions</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="impact-visual-image">
                        <img src={farmerImage} alt="Cameroon farmer using PlumVision" />
                      </div>
                    </div>
            </section>

            <section className='features-section' id="features">
                {features.map((feature, idx) => (
                    <div key={idx} className={`feature ${feature.reversed ? 'reversed' : ''}`}>
                        <div className="img-box">
                            <Suspense fallback={<div className="placeholder-loading"></div>}>
                                <LazyImage 
                                    src={feature.gif} 
                                    placeholder={placeholder}
                                    alt={feature.title}
                                    data-aos="fade-in"
                                    data-aos-duration="300"
                                />
                            </Suspense>
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