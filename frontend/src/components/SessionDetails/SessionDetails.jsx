import React from 'react';
import './SessionDetails.css';
import { FiRefreshCw } from 'react-icons/fi';
import { Doughnut } from 'react-chartjs-2';

const SessionDetails = ({ session, onBack }) => {
  if (!session) return null;

  // Prepare chart data for doughnut
  const prepareCategoryChartData = () => {
    if (!session.predictions_by_category) return null;
    
    const categories = Object.keys(session.predictions_by_category);
    const counts = Object.values(session.predictions_by_category);
    
    // Color mapping based on category
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

  // Chart options
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

  const categoryChartData = prepareCategoryChartData();

  return (
    <div className="session-details">
      <div className="session-details-header">
        <h3 className="m-font">Session Details: {session.session_id}</h3>
        <button 
          className="icon-btn back-btn" 
          onClick={onBack}
        >
          <FiRefreshCw size={18} />
          <span>Back to Live View</span>
        </button>
      </div>
      
      <div className="session-metrics">
        <div className="session-info-grid">
          <div className="stat-card">
            <h4>Total Images</h4>
            <p className="stat-value">{session.total_images_processed}</p>
          </div>
          
          <div className="stat-card">
            <h4>Duration</h4>
            <p className="stat-value">
              {session.duration_seconds ? 
                `${Math.floor(session.duration_seconds / 60)}m ${session.duration_seconds % 60}s` : 
                'Active'}
            </p>
          </div>
          
          <div className="stat-card">
            <h4>Status</h4>
            <p className={`stat-value ${session.is_active ? 'active-status' : 'inactive-status'}`}>
              {session.is_active ? 'Active' : 'Completed'}
            </p>
          </div>
          
          <div className="stat-card">
            <h4>Started</h4>
            <p className="stat-value">{new Date(session.start_time).toLocaleTimeString()}</p>
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
                {session.predictions_by_class && Object.entries(session.predictions_by_class).map(([className, count]) => (
                  <div className="class-item" key={className}>
                    <span className="class-name">{className}</span>
                    <div className="class-bar-container">
                      <div 
                        className="class-bar" 
                        style={{ 
                          width: `${(count / session.total_images_processed) * 100}%`,
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
    </div>
  );
};

export default SessionDetails;