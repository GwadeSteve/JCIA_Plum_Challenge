import React from 'react';
import './PredictionGraph.css';

const PredictionGraph = ({ predictions }) => {
  const classNameMapping = {
    'unaffected': 'Healthy',
    'unripe': 'Unripe',
    'rotten': 'Rotten',
    'spotted': 'Spotted',
    'cracked': 'Cracked', 
    'bruised': 'Bruised'
  };
  
  const superclassMapping = {
    'Healthy': 'Good',
    'Unripe': 'Unripe',
    'Rotten': 'Defective',
    'Spotted': 'Defective',
    'Cracked': 'Defective',
    'Bruised': 'Defective'
  };
  
  const superclassColorMap = {
    'Good': '#54C747',
    'Unripe': '#E2DA00',
    'Defective': '#FF5757'
  };
  
  const categories = [
    'Healthy',
    'Unripe',
    'Rotten',
    'Spotted',
    'Cracked',
    'Bruised'
  ];
  
  const colorMap = {
    'Healthy': '#54C747',
    'Unripe': '#E2DA00',
    'Rotten': '#FF5757',
    'Spotted': '#ff9500',
    'Cracked': '#af52de',
    'Bruised': '#1F87E1'
  };

  const normalizedPredictions = categories.map(category => {
    const matchedPrediction = predictions && predictions.find(p => {
      if (!p.class) return false;
      const displayClass = classNameMapping[p.class.toLowerCase()] || p.class;
      return displayClass.toLowerCase() === category.toLowerCase();
    });
    
    return {
      class: category,
      probability: matchedPrediction ? 
        (typeof matchedPrediction.probability === 'string' ? 
          parseFloat(matchedPrediction.probability) : 
          matchedPrediction.probability) : 
        0
    };
  });

  const maxPrediction = normalizedPredictions.reduce(
    (max, current) => (current.probability > max.probability ? current : max),
    { probability: 0 }
  );
  
  const superclass = maxPrediction.probability > 0 
    ? superclassMapping[maxPrediction.class] || 'Unknown'
    : 'Unknown';
  
  const superclassColor = superclassColorMap[superclass] || colorMap[maxPrediction.class] || '#6c00fa';

  //console.log('Original predictions:', predictions);
  //console.log('Normalized predictions:', normalizedPredictions);
  //console.log('Superclass:', superclass);

  return (
    <div className="prediction-graph">
      {normalizedPredictions.map((pred, index) => {
        const color = colorMap[pred.class] || '#6c00fa';
        
        return (
          <div key={index} className="prediction-bar-container">
            <div className="bar-label">
              <div className="category-label">
                <span 
                  className="color-indicator" 
                  style={{ backgroundColor: color }}
                ></span>
                <span className="category-name">{pred.class}</span>
              </div>
              <span className="percentage">{(pred.probability * 100).toFixed(1)}%</span>
            </div>
            <div className="bar-background">
              <div 
                className={`bar-fill ${pred.probability === maxPrediction.probability && pred.probability > 0 ? 'highest' : ''}`}
                style={{ 
                  width: `${pred.probability * 100}%`,
                  backgroundColor: color
                }}
              ></div>
            </div>
          </div>
        );
      })}
      
      {maxPrediction.probability > 0 && (
        <div className="prediction-summary">
          <p>Plum condition: <strong style={{ color: superclassColor }}>{superclass}</strong> ({(maxPrediction.probability * 100).toFixed(1)}% {maxPrediction.class})</p>
        </div>
      )}
    </div>
  );
};

export default PredictionGraph;