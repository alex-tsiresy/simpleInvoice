import React, { useState } from 'react';
import './DocumentCard.css';

function DocumentCard({ document, onDelete }) {
  const [showOCRText, setShowOCRText] = useState(false);

  const getStatusBadge = (status) => {
    const badges = {
      uploaded: { text: 'Uploaded', class: 'status-uploaded' },
      processing: { text: 'Processing', class: 'status-processing' },
      ocr_complete: { text: 'OCR Complete', class: 'status-ocr' },
      completed: { text: 'Completed', class: 'status-completed' },
      failed: { text: 'Failed', class: 'status-failed' }
    };
    return badges[status] || { text: status, class: 'status-unknown' };
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${document.original_filename}"?`)) {
      onDelete(document.id);
    }
  };

  const statusBadge = getStatusBadge(document.status);
  const invoiceData = document.invoice_data;

  return (
    <div className="document-card">
      <div className="card-header">
        <div className="card-badges">
          <span className={`status-badge ${statusBadge.class}`}>
            {statusBadge.text}
          </span>
          {invoiceData && (
            <span className="type-badge type-invoice">
              📋 Invoice
            </span>
          )}
        </div>
      </div>

      <div className="card-body">
        <h4 className="document-filename" title={document.original_filename}>
          {document.original_filename}
        </h4>

        <div className="document-meta">
          <p><strong>File Type:</strong> {document.file_type}</p>
          <p><strong>Size:</strong> {formatFileSize(document.file_size)}</p>
          <p><strong>Uploaded:</strong> {formatDate(document.created_at)}</p>
        </div>

        {/* Invoice Data Display */}
        {invoiceData && (
          <div className="invoice-data">
            <h5 className="invoice-header">📋 Invoice Information</h5>

            <div className="invoice-grid">
              {/* Key Invoice Details */}
              <div className="invoice-section">
                <h6>Invoice Details</h6>
                {invoiceData.invoice_number && (
                  <p><strong>Invoice #:</strong> {invoiceData.invoice_number}</p>
                )}
                {invoiceData.invoice_date && (
                  <p><strong>Date:</strong> {invoiceData.invoice_date}</p>
                )}
                {invoiceData.due_date && (
                  <p><strong>Due Date:</strong> {invoiceData.due_date}</p>
                )}
                {invoiceData.payment_terms && (
                  <p><strong>Payment Terms:</strong> {invoiceData.payment_terms}</p>
                )}
              </div>

              {/* Financial Information */}
              <div className="invoice-section">
                <h6>Financial Summary</h6>
                {invoiceData.subtotal && (
                  <p><strong>Subtotal:</strong> {invoiceData.subtotal}</p>
                )}
                {invoiceData.tax_amount && (
                  <p><strong>Tax:</strong> {invoiceData.tax_amount}</p>
                )}
                {invoiceData.total_amount && (
                  <p className="invoice-total"><strong>Total:</strong> {invoiceData.total_amount} {invoiceData.currency || ''}</p>
                )}
              </div>

              {/* Sender Information */}
              {invoiceData.sender && (
                <div className="invoice-section">
                  <h6>From (Sender)</h6>
                  {invoiceData.sender.name && (
                    <p><strong>Name:</strong> {invoiceData.sender.name}</p>
                  )}
                  {invoiceData.sender.address && (
                    <p><strong>Address:</strong> {invoiceData.sender.address}</p>
                  )}
                  {invoiceData.sender.email && (
                    <p><strong>Email:</strong> {invoiceData.sender.email}</p>
                  )}
                  {invoiceData.sender.phone && (
                    <p><strong>Phone:</strong> {invoiceData.sender.phone}</p>
                  )}
                  {invoiceData.sender.tax_id && (
                    <p><strong>Tax ID:</strong> {invoiceData.sender.tax_id}</p>
                  )}
                </div>
              )}

              {/* Receiver Information */}
              {invoiceData.receiver && (
                <div className="invoice-section">
                  <h6>To (Receiver)</h6>
                  {invoiceData.receiver.name && (
                    <p><strong>Name:</strong> {invoiceData.receiver.name}</p>
                  )}
                  {invoiceData.receiver.address && (
                    <p><strong>Address:</strong> {invoiceData.receiver.address}</p>
                  )}
                  {invoiceData.receiver.email && (
                    <p><strong>Email:</strong> {invoiceData.receiver.email}</p>
                  )}
                  {invoiceData.receiver.phone && (
                    <p><strong>Phone:</strong> {invoiceData.receiver.phone}</p>
                  )}
                  {invoiceData.receiver.tax_id && (
                    <p><strong>Tax ID:</strong> {invoiceData.receiver.tax_id}</p>
                  )}
                </div>
              )}
            </div>

            {/* Notes */}
            {invoiceData.notes && (
              <div className="invoice-notes">
                <strong>Notes:</strong>
                <p>{invoiceData.notes}</p>
              </div>
            )}
          </div>
        )}

        {/* OCR Text Toggle */}
        {document.ocr_text && (
          <div className="ocr-preview">
            <button
              className="toggle-details"
              onClick={() => setShowOCRText(!showOCRText)}
            >
              {showOCRText ? 'Hide' : 'Show'} OCR Text
            </button>

            {showOCRText && (
              <div className="ocr-text">
                <p>{document.ocr_text.substring(0, 1000)}...</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card-footer">
        <button className="btn-delete" onClick={handleDelete}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Delete
        </button>
      </div>
    </div>
  );
}

export default DocumentCard;
