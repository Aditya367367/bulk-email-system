import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onFileUpload, isLoading, dailyLimit }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false,
    disabled: isLoading || dailyLimit.remaining_emails === 0
  });

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800 font-semibold">Daily email limit is 100</p>
        <p className="text-blue-600 text-sm">
          Today's usage: {dailyLimit.emails_sent} / {dailyLimit.emails_sent + dailyLimit.remaining_emails}
        </p>
        <p className="text-blue-600 text-sm">
          Remaining emails: {dailyLimit.remaining_emails}
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${isLoading || dailyLimit.remaining_emails === 0 ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {isLoading ? (
          <div className="space-y-2">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600">Uploading file...</p>
          </div>
        ) : (
          <div className="space-y-2">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            
            {isDragActive ? (
              <p className="text-blue-600">Drop the Excel file here...</p>
            ) : (
              <div>
                <p className="text-gray-600">Drag and drop an Excel file here, or click to select</p>
                <p className="text-gray-400 text-sm mt-1">Supported formats: .xlsx, .xls</p>
                <p className="text-gray-400 text-sm">Maximum 100 rows per file</p>
              </div>
            )}
          </div>
        )}
      </div>

      {dailyLimit.remaining_emails === 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">
            Daily email limit reached. Please try again tomorrow.
          </p>
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-semibold text-gray-700 mb-2">Required Excel Columns:</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>name</li>
          <li>email</li>
          <li>license_number</li>
          <li>validity_from</li>
          <li>premises_type</li>
          <li>category</li>
          <li>address</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUpload;
