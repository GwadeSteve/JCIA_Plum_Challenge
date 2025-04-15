import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUpload } from 'react-icons/fi';
import './DropZoneUploader.css';

const DropZoneUploader = ({ onImageUpload }) => {
  const [isDragging, setIsDragging] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      const imageUrl = URL.createObjectURL(file);
      onImageUpload(file, imageUrl);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif']
    },
    maxFiles: 1,
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
    onDropAccepted: () => setIsDragging(false),
    onDropRejected: () => setIsDragging(false)
  });

  return (
    <div 
      {...getRootProps()} 
      className={`dropzone ${isDragging ? 'active' : ''}`}
    >
      <input {...getInputProps()} />
      <FiUpload size={48} className="upload-icon" />
      <p>Drag & drop a plum image here, or click to select</p>
      <p className="xs-font">Supported formats: JPG, PNG, GIF</p>
    </div>
  );
};

export default DropZoneUploader;