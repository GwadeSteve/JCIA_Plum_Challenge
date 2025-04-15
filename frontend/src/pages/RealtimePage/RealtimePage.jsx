import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiCamera, FiPause, FiPlay, FiVideo, FiX, FiBarChart2, FiClock, FiRefreshCw } from 'react-icons/fi';
import './RealtimePage.css';
import { connectToStreamSession } from '../../utilities/api';
import PredictionGraph from '../../components/PredictionGraph/PredictionGraph';
import SessionDetails from '../../components/SessionDetails/SessionDetails';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const RealtimePage = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessionStats, setSessionStats] = useState(null);
  const [streamingFeedback, setStreamingFeedback] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [pastSessions, setPastSessions] = useState([]);
  const [showPastSessions, setShowPastSessions] = useState(false);
  const [lastPrediction, setLastPrediction] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [viewMode, setViewMode] = useState('live'); // 'live', 'details'
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const websocketRef = useRef(null);
  const captureIntervalRef = useRef(null);
  const navigate = useNavigate();

  const formatTime = useCallback((timestamp, includeSeconds = false) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const adjustedDate = new Date(date.getTime() + (60 * 60 * 1000));
    
    const options = {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
      ...(includeSeconds ? { second: '2-digit' } : {})
    };

    
    
    return adjustedDate.toLocaleTimeString(undefined, options);
  }, []);

  const formatDate = useCallback((timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    // Fix timezone by adding one hour
    const adjustedDate = new Date(date.getTime() + (60 * 60 * 1000));
    
    return adjustedDate.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }, []);

  const displayPopup = useCallback((message) => {
    setPopupMessage(message);
    setShowPopup(true);
    setTimeout(() => setShowPopup(false), 3000);
  }, []);

  const stopAllTracks = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  const stopStreaming = useCallback(() => {
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current);
      captureIntervalRef.current = null;
    }

    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.close();
      websocketRef.current = null;
    }

    stopAllTracks();
    
    setIsStreaming(false);
    setStreamingFeedback(null);
  }, [stopAllTracks]);

  const handlePredictionResult = useCallback((data) => {
    if (data.prediction && data.prediction.prediction && data.prediction.prediction.length > 0) {
      const topPrediction = data.prediction.prediction[0];
      
      if (isStreaming) {
        const now = new Date();
        setStreamingFeedback({
          className: topPrediction.class,
          probability: topPrediction.probability,
          timestamp: now.toLocaleTimeString(undefined, {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
          })
        });
      }
      
      setLastPrediction(data.prediction.prediction);
      
      if (data.session_stats) {
        setSessionStats(data.session_stats);
      }
    }
  }, [isStreaming]);

  const initWebsocket = useCallback(() => {
    try {
      const ws = connectToStreamSession();
      websocketRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connection established');
        displayPopup('Stream session connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);

        if (data.status === 'connected') {
          setSessionId(data.session_id);
          displayPopup('Stream session started');
        } else if (data.status === 'prediction_result') {
          handlePredictionResult(data);
        } else if (data.status === 'closing') {
          displayPopup(`Stream closing: ${data.reason}`);
          stopStreaming();
        } else if (data.status === 'error') {
          displayPopup(`Error: ${data.message}`);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
        stopStreaming();
        displayPopup('Stream session ended');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        displayPopup('WebSocket error occurred');
        stopStreaming();
      };

      return ws;
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      displayPopup('Failed to connect to server');
      return null;
    }
  }, [displayPopup, stopStreaming, handlePredictionResult]);

  const startCamera = useCallback(async () => {
    try {
      if (streamRef.current) {
        stopAllTracks();
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });

      streamRef.current = mediaStream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error accessing camera:', error);
      displayPopup('Could not access camera');
      return false;
    }
  }, [stopAllTracks, displayPopup]);

  const captureAndSendFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !websocketRef.current || 
        websocketRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob && websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        const reader = new FileReader();
        reader.onloadend = () => {
          const arrayBuffer = reader.result;
          websocketRef.current.send(arrayBuffer);
        };
        reader.readAsArrayBuffer(blob);
      }
    }, 'image/jpeg', 0.8);
  }, []);

  const startStreaming = useCallback(async () => {
    setViewMode('live');
    setSelectedSession(null);
    
    const cameraStarted = await startCamera();
    
    if (!cameraStarted) {
      displayPopup('Failed to start camera');
      return;
    }

    const ws = initWebsocket();
    if (!ws) return;

    setIsStreaming(true);
    setSessionStats(null);
    setStreamingFeedback(null);
    setLastPrediction(null);

    captureIntervalRef.current = setInterval(() => {
      captureAndSendFrame();
    }, 500);
  }, [startCamera, captureAndSendFrame, initWebsocket, displayPopup]);

  const loadPastSessions = useCallback(async () => {
    try {
      const sessionsData = await fetch('http://localhost:8000/api/sessions').then(res => res.json());
      setPastSessions(sessionsData);
      setShowPastSessions(true);
    } catch (error) {
      console.error('Error loading past sessions:', error);
      displayPopup('Failed to load past sessions');
    }
  }, [displayPopup]);

  const viewSessionDetails = useCallback((id) => {
    if (id) {
      setSelectedSession(id);
      setViewMode('details');
      fetch(`http://localhost:8000/api/metrics/${id}`)
        .then(res => res.json())
        .then(data => {
          console.log("Session details:", data);
          setSessionStats(data);
        })
        .catch(error => {
          console.error('Error loading session details:', error);
          displayPopup('Failed to load session details');
        });
    } else if (sessionId) {
      setSelectedSession(sessionId);
      setViewMode('details');
    } else {
      displayPopup('No active session');
    }
  }, [sessionId, displayPopup]);

  const togglePastSessions = useCallback(() => {
    if (!showPastSessions) {
      loadPastSessions();
    } else {
      setShowPastSessions(false);
    }
  }, [showPastSessions, loadPastSessions]);

  const getRelativeTime = (timestamp) => {
    const now = new Date();
    const time = new Date(new Date(timestamp).getTime() + (60 * 60 * 1000));
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) {
      return `${diffInSeconds} seconds ago`;
    } else if (diffInSeconds < 3600) {
      return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    } else if (diffInSeconds < 86400) {
      return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    } else {
      return `${Math.floor(diffInSeconds / 86400)} days ago`;
    }
  };

  const returnToLiveView = useCallback(() => {
    setViewMode('live');
    setSelectedSession(null);
  }, []);

  useEffect(() => {
    return () => {
      stopStreaming();
    };
  }, [stopStreaming]);

  const prepareCategoryChartData = (stats) => {
    if (!stats || !stats.predictions_by_category) return null;
    
    const categories = Object.keys(stats.predictions_by_category);
    const counts = Object.values(stats.predictions_by_category);
    
    const backgroundColors = categories.map(category => {
      switch(category) {
        case 'Good': return '#54C747';
        case 'Unripe': return '#E2DA00';
        case 'Defective': return '#FF5757';
        default: return '#6c00fa';
      }
    });
    
    return {
      labels: categories,
      datasets: [
        {
          data: counts,
          backgroundColor: backgroundColors,
          borderColor: backgroundColors.map(color => color + '80'),
          borderWidth: 1,
        },
      ],
    };
  };

  const chartOptions = {
    plugins: {
      legend: {
        position: 'right',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.raw || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = Math.round((value / total) * 100);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
    cutout: '70%',
    responsive: true,
    maintainAspectRatio: false,
  };

  const categoryChartData = sessionStats ? prepareCategoryChartData(sessionStats) : null;

  const truncateId = (id) => {
    if (!id) return '';
    if (id.length <= 8) return id;
    return `${id.substring(0, 4)}...${id.substring(id.length - 4)}`;
  };

  return (
    <div className="RealtimePage">
      <div className="stream-container">
        <div className="main-content">
          {viewMode === 'live' ? (
            <>
              <div className="video-feed">
                <video ref={videoRef} autoPlay playsInline muted />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
                
                {!isStreaming && (
                  <div className="stream-placeholder">
                    <FiVideo size={60} />
                    <p>Start streaming to analyze plums in real-time</p>
                  </div>
                )}
                
                {isStreaming && streamingFeedback && (
                  <div className="stream-feedback">
                    <p>Last Detected: <strong>{streamingFeedback.className}</strong> ({(streamingFeedback.probability * 100).toFixed(1)}%)</p>
                    <p className="timestamp">{streamingFeedback.timestamp}</p>
                  </div>
                )}
              </div>

              {lastPrediction && (
                <div className="live-prediction">
                  <h3 className="m-font">Live Prediction</h3>
                  <div className="prediction-graph-container">
                    <PredictionGraph predictions={lastPrediction} />
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="session-details-container">
              <div className="session-details-header">
                <h3 className="m-font">Session Details: {truncateId(selectedSession)}</h3>
                <button 
                  className="icon-btn back-btn filled-black" 
                  onClick={returnToLiveView}
                >
                  <FiRefreshCw size={18} />
                  <span>Back to Live</span>
                </button>
              </div>
              
              {sessionStats && (
                <div className="session-metrics">
                  <div className="session-info-grid">
                    <div className="stat-card">
                      <h4>Total Images</h4>
                      <p className="stat-value">{sessionStats.total_images_processed}</p>
                    </div>
                    
                    <div className="stat-card">
                      <h4>Duration</h4>
                      <p className="stat-value">
                        {sessionStats.duration_seconds ? 
                          `${Math.floor(sessionStats.duration_seconds / 60)}m ${sessionStats.duration_seconds % 60}s` : 
                          'Active'}
                      </p>
                    </div>
                    
                    <div className="stat-card">
                      <h4>Status</h4>
                      <p className={`stat-value ${sessionStats.is_active ? 'active-status' : 'inactive-status'}`}>
                        {sessionStats.is_active ? 'Active' : 'Completed'}
                      </p>
                    </div>
                    
                    <div className="stat-card">
                      <h4>Started</h4>
                      <p className="stat-value">
                        {formatTime(sessionStats.start_time, true)}
                      </p>
                    </div>
                  </div>
                  
                  {categoryChartData && (
                    <div className="charts-container">
                      <div className="chart-card">
                        <h4>Category Distribution</h4>
                        <div className="chart-wrapper">
                          <Doughnut data={categoryChartData} options={chartOptions} />
                        </div>
                      </div>
                      
                      <div className="prediction-classes">
                        <h4>Class Distribution</h4>
                        <div className="class-list">
                          {sessionStats.predictions_by_class && Object.entries(sessionStats.predictions_by_class).map(([className, count]) => (
                            <div className="class-item" key={className}>
                              <span className="class-name">{className}</span>
                              <div className="class-bar-container">
                                <div 
                                  className="class-bar" 
                                  style={{ 
                                    width: `${(count / sessionStats.total_images_processed) * 100}%`,
                                    backgroundColor: className.toLowerCase() === 'unaffected' ? '#54C747' : 
                                                    className.toLowerCase() === 'unripe' ? '#E2DA00' : '#FF5757'
                                  }} 
                                ></div>
                              </div>
                              <span className="class-count">{count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="controls-panel">
          <h2 className="l-font">Real-time Plum Analysis</h2>
          
          <div className="control-buttons">
            {!isStreaming ? (
              <button className="filled-violet" onClick={startStreaming}>
                <FiPlay size={20} />
                <span>Start Streaming</span>
              </button>
            ) : (
              <button className="stop-btn" onClick={stopStreaming}>
                <FiPause size={20} />
                <span>Stop Streaming</span>
              </button>
            )}
            
            <div className="btn-row">
              <button 
                className="border-violet" 
                onClick={() => viewSessionDetails()}
                disabled={!sessionId}
              >
                <FiBarChart2 size={20} />
                <span>View Current Session</span>
              </button>
              
              <button 
                className={`${showPastSessions ? 'filled-black' : 'border-black'}`}
                onClick={togglePastSessions}
              >
                <FiClock size={20} />
                <span>{showPastSessions ? 'Hide Past Sessions' : 'View Past Sessions'}</span>
              </button>
            </div>
            
            <button 
              className="border-black" 
              onClick={() => navigate('/demo')}
            >
              <FiCamera size={20} />
              <span>Switch to Single Image</span>
            </button>
          </div>
          
          {sessionStats && viewMode === 'live' && (
            <div className="session-stats">
              <h3 className="m-font">Current Session Stats</h3>
              
              <div className="total-images">
                <span className="stat-label">Images Processed</span>
                <span className="stat-value">{sessionStats.total_images_processed}</span>
              </div>
              
              {sessionStats.predictions_by_category && Object.keys(sessionStats.predictions_by_category).length > 0 && (
                <div className="category-chart">
                  <span className="stat-label">Categories</span>
                  <div className="chart-container" style={{ height: '200px' }}>
                    {categoryChartData && <Doughnut data={categoryChartData} options={chartOptions} />}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {showPastSessions && (
            <div className="past-sessions">
              <h3 className="m-font">Past Sessions</h3>
              {pastSessions.length > 0 ? (
                <div className="sessions-list">
                  {pastSessions.map((session) => (
                    <div 
                      key={session.session_id} 
                      className={`session-item ${selectedSession === session.session_id ? 'selected' : ''}`}
                    >
                      <div className="session-info">
                        <div className="session-main-info">
                          <div className="session-date">
                            {formatDate(session.start_time)}
                          </div>
                          <div className="session-time">
                            {formatTime(session.start_time)}
                          </div>
                        </div>
                        <div className="session-meta">
                          <span className="session-ago">{getRelativeTime(session.start_time)}</span>
                          <span className="session-count">{session.total_images_processed} images</span>
                        </div>
                      </div>
                      <button 
                        className="view-session-btn"
                        onClick={() => viewSessionDetails(session.session_id)}
                      >
                        View
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-sessions">
                  <p>No past sessions found</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {showPopup && (
        <div className="popup-notification">
          <div className="popup-content">
            <span>{popupMessage}</span>
            <button onClick={() => setShowPopup(false)}>
              <FiX size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealtimePage;