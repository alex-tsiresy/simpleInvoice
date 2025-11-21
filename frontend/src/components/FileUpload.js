import React, { useState, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

function FileUpload({ onUploadComplete }) {
  const { getToken } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);
    setUploadProgress({ name: file.name, status: 'Uploading...' });

    try {
      const token = await getToken();
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/documents/upload`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setUploadProgress({
        name: file.name,
        status: 'Uploaded successfully! Processing...'
      });

      // Notify parent component
      setTimeout(() => {
        setUploadProgress(null);
        if (onUploadComplete) {
          onUploadComplete(data.document);
        }
      }, 2000);

    } catch (err) {
      setError(err.message);
      setUploadProgress(null);
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  }, [getToken, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff', '.tif'],
      'image/bmp': ['.bmp']
    },
    maxFiles: 1,
    disabled: uploading
  });

  return (
    <div className="file-upload-container">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          {uploading ? (
            <>
              <div className="spinner"></div>
              <p className="upload-text">Uploading...</p>
            </>
          ) : isDragActive ? (
            <>
              <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="upload-text">Drop file here</p>
            </>
          ) : (
            <>
              <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="upload-text">Drag & drop a file here, or click to select</p>
              <p className="upload-hint">Supported: PDF, PNG, JPG, TIFF, BMP</p>
            </>
          )}
        </div>
      </div>

      {uploadProgress && (
        <div className="upload-progress">
          <p className="progress-filename">{uploadProgress.name}</p>
          <p className="progress-status">{uploadProgress.status}</p>
        </div>
      )}

      {error && (
        <div className="upload-error">
          <p>Upload failed: {error}</p>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
