import React, { useState } from 'react';
import './PredictionPage.css';
import { useNavigate } from 'react-router-dom';
import { FiCamera, FiRefreshCw, FiVideo } from 'react-icons/fi';
import DropZoneUploader from '../../components/DropZoneUploader/DropZoneUploader';
import ImagePreview from '../../components/ImagePreview/ImagePreview';
import PredictButton from '../../components/PredictButton/PredictButton';
import PredictionGraph from '../../components/PredictionGraph/PredictionGraph';
import CameraCapture from '../../components/CameraCapture/CameraCapture';
import { predictImage } from '../../utilities/api';

const CustomButton = ({ children, variant, link, onClick, icon }) => {
    const navigate = useNavigate();

    const handleClick = () => {
        if (link && link !== '#') {
            navigate(link);
        }
        if (onClick) {
            onClick();
        }
    };

    return (
        <button className={variant} onClick={handleClick}>
            {icon && icon}
            <span>{children}</span>
        </button>
    );
};

const PredictionPage = () => {
    const [imageFile, setImageFile] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [showCamera, setShowCamera] = useState(false);
    const [predictions, setPredictions] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleImageUpload = (file, previewUrl) => {
        setImageFile(file);
        setImagePreview(previewUrl);
        setPredictions(null);
    };

    const handleCameraCapture = (file, previewUrl) => {
        setImageFile(file);
        setImagePreview(previewUrl);
        setShowCamera(false);
        setPredictions(null); 
    };

    const handleRemoveImage = () => {
        setImageFile(null);
        setImagePreview(null);
        setPredictions(null);
    };

    const handlePredict = async () => {
        if (!imageFile) return;

        setIsLoading(true);
        try {
            const result = await predictImage(imageFile);
            if (result.prediction) {
                setPredictions(result.prediction);
            }
        } catch (error) {
            console.error('Prediction failed:', error);
            alert('Failed to predict image. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleRestart = () => {
        setImageFile(null);
        setImagePreview(null);
        setPredictions(null);
    };

    return (
        <div className='PredictionPage'>
            <div className="uploader">
                {showCamera ? (
                    <CameraCapture 
                        onCapture={handleCameraCapture} 
                        onClose={() => setShowCamera(false)} 
                    />
                ) : (
                    <>
                        {imagePreview ? (
                            <>
                                <ImagePreview 
                                    imageUrl={imagePreview} 
                                    onRemove={handleRemoveImage} 
                                />
                                <PredictButton 
                                    onClick={handlePredict} 
                                    isLoading={isLoading} 
                                />
                            </>
                        ) : (
                            <>
                                <DropZoneUploader onImageUpload={handleImageUpload} />
                                <button 
                                    className="camera-trigger"
                                    onClick={() => setShowCamera(true)}
                                >
                                    <FiCamera size={20} />
                                    <span>Capture with Camera</span>
                                </button>
                            </>
                        )}
                    </>
                )}
            </div>
            <div className="results">
                <h2 className='l-font'>Predictions</h2>
                <div className="graph">
                    <PredictionGraph predictions={predictions} />
                </div>
                <div className="quick-btns">
                    <CustomButton 
                        variant="border-black" 
                        link="#" 
                        onClick={handleRestart}
                        icon={<FiRefreshCw size={18} />}
                    >
                        Restart
                    </CustomButton>
                    <CustomButton 
                        variant="filled-black" 
                        link="/realtime"
                        icon={<FiVideo size={18} />}
                    >
                        Stream Session
                    </CustomButton>
                </div>
            </div>
        </div>
    );
};

export default PredictionPage;