import React, { useState } from 'react';
import DocumentCard from './DocumentCard';
import './DocumentList.css';

function DocumentList({ documents, loading, onDelete, onRefresh }) {
  const [filter, setFilter] = useState('all');

  const filteredDocuments = documents.filter(doc => {
    if (filter === 'all') return true;
    return doc.document_type === filter;
  });

  const getStatusCounts = () => {
    const counts = {
      all: documents.length,
      invoice: 0,
      contract: 0,
      meeting_minutes: 0,
      email: 0
    };

    documents.forEach(doc => {
      if (counts.hasOwnProperty(doc.document_type)) {
        counts[doc.document_type]++;
      }
    });

    return counts;
  };

  const counts = getStatusCounts();

  return (
    <div className="document-list-container">
      <div className="list-header">
        <div className="list-title">
          <h3>Your Documents</h3>
          <button className="refresh-button" onClick={onRefresh} disabled={loading}>
            <svg className="refresh-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>

        <div className="filter-tabs">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All ({counts.all})
          </button>
          <button
            className={filter === 'invoice' ? 'active' : ''}
            onClick={() => setFilter('invoice')}
          >
            Invoices ({counts.invoice})
          </button>
          <button
            className={filter === 'contract' ? 'active' : ''}
            onClick={() => setFilter('contract')}
          >
            Contracts ({counts.contract})
          </button>
          <button
            className={filter === 'meeting_minutes' ? 'active' : ''}
            onClick={() => setFilter('meeting_minutes')}
          >
            Minutes ({counts.meeting_minutes})
          </button>
          <button
            className={filter === 'email' ? 'active' : ''}
            onClick={() => setFilter('email')}
          >
            Emails ({counts.email})
          </button>
        </div>
      </div>

      {loading && documents.length === 0 ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading documents...</p>
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="empty-state">
          <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No documents found</p>
          <p className="empty-hint">Upload a document to get started</p>
        </div>
      ) : (
        <div className="documents-grid">
          {filteredDocuments.map(doc => (
            <DocumentCard
              key={doc.id}
              document={doc}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentList;
