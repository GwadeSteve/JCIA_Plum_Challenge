import React from 'react';
import { FiX } from 'react-icons/fi';
import './ImagePreview.css';

const ImagePreview = ({ imageUrl, onRemove }) => {
  return (
    <div className="image-preview-container">
      <button className="remove-image-btn" onClick={onRemove}>
        <FiX size={20} />
      </button>
      <img src={imageUrl} alt="Preview" className="image-preview" />
    </div>
  );
};

export default ImagePreview;