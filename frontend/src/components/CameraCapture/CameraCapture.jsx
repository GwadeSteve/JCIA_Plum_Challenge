import React, { useRef, useState, useEffect, useCallback } from 'react';
import { FiCamera, FiX } from 'react-icons/fi';
import './CameraCapture.css';

const CameraCapture = ({ onCapture, onClose }) => {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  const stopAllTracks = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
      });
      streamRef.current = null;
    }
  }, []);

  const handleClose = useCallback(() => {
    stopAllTracks();
    if (onClose) onClose();
  }, [stopAllTracks, onClose]);

  useEffect(() => {
    let isMounted = true;
    
    const initCamera = async () => {
      stopAllTracks();
      
      try {
        const constraints = { 
          video: { 
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 }
          } 
        };
        
        const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        streamRef.current = mediaStream;
        
        if (isMounted && videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          
          videoRef.current.onloadedmetadata = () => {
            if (videoRef.current) {
              videoRef.current.play()
                .then(() => {
                  if (isMounted) setIsReady(true);
                })
                .catch(err => {
                  console.error("Error playing video:", err);
                });
            }
          };
        } else {
          stopAllTracks();
        }
      } catch (error) {
        console.error("Error accessing camera:", error);
        alert("Could not access camera. Please make sure you've granted camera permissions.");
        if (isMounted && onClose) onClose();
      }
    };

    initCamera();
    
    return () => {
      isMounted = false;
      stopAllTracks();
    };
  }, [onClose, stopAllTracks]);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !isReady || !streamRef.current) return;
    
    const video = videoRef.current;
    
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const dataUrl = canvas.toDataURL('image/jpeg', 1.0);
    
    fetch(dataUrl)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
        
        stopAllTracks();
        
        onCapture(file, dataUrl);
      })
      .catch(error => {
        console.error("Error creating file from canvas:", error);
        alert("Failed to capture image. Please try again.");
      });
  }, [isReady, onCapture, stopAllTracks]);

  return (
    <div className="camera-container">
      <div className="camera-header">
        <h3>Camera Capture</h3>
        <button type="button" className="close-btn" onClick={handleClose}>
          <FiX size={24} />
        </button>
      </div>
      
      <div className="video-container">
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          muted 
          className="camera-preview"
        />
        
        {!isReady && (
          <div className="camera-loading">
            <div className="loading-spinner"></div>
            <p>Accessing camera...</p>
          </div>
        )}
      </div>
      
      <button 
        type="button"
        className="capture-button" 
        onClick={captureImage}
        disabled={!isReady}
      >
        <FiCamera size={24} />
        <span>Capture</span>
      </button>
    </div>
  );
};

export default CameraCapture;