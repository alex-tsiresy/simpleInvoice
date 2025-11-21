import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import FileUpload from './FileUpload';
import DocumentList from './DocumentList';
import './Dashboard.css';

function Dashboard() {
  const { getToken } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const token = await getToken();
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/documents`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }

      const data = await response.json();
      setDocuments(data.documents || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  useEffect(() => {
    fetchDocuments();
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchDocuments, 5000);
    return () => clearInterval(interval);
  }, [fetchDocuments]);

  const handleUploadComplete = () => {
    fetchDocuments();
  };

  const handleDelete = async (documentId) => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/documents/${documentId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete document');
      }

      fetchDocuments();
    } catch (err) {
      alert('Error deleting document: ' + err.message);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Document Processing Dashboard</h2>
        <p>Upload documents for OCR processing and classification</p>
      </div>

      <FileUpload onUploadComplete={handleUploadComplete} />

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={fetchDocuments}>Retry</button>
        </div>
      )}

      <DocumentList
        documents={documents}
        loading={loading}
        onDelete={handleDelete}
        onRefresh={fetchDocuments}
      />
    </div>
  );
}

export default Dashboard;
