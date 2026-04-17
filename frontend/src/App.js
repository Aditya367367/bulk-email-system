import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import ProgressTracker from './components/ProgressTracker';
import StatusCards from './components/StatusCards';
import JobHistory from './components/JobHistory';
import './App.css';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [currentJob, setCurrentJob] = useState(null);
  const [dailyLimit, setDailyLimit] = useState({ emails_sent: 0, remaining_emails: 100 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchDailyLimit();
    fetchJobHistory();
  }, []);

  const fetchDailyLimit = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/daily-limit/`);
      setDailyLimit(response.data);
    } catch (err) {
      console.error('Error fetching daily limit:', err);
    }
  };

  const fetchJobHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs/`);
      // Update job history component if needed
    } catch (err) {
      console.error('Error fetching job history:', err);
    }
  };

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('excel_file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setCurrentJob(response.data);
      setSuccess('Excel file uploaded successfully!');
      fetchDailyLimit();
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
    } finally {
      setIsLoading(false);
    }
  };

  const startEmailSending = async () => {
    if (!currentJob) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/start/${currentJob.job_id}/`);
      setSuccess('Email sending started!');
      // Start polling for status updates
      pollJobStatus(currentJob.job_id);
    } catch (err) {
      setError(err.response?.data?.error || 'Error starting email sending');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJobUpdate = (updatedJob) => {
    setCurrentJob(prev => ({ ...prev, ...updatedJob }));
  };

  const pollJobStatus = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/status/${jobId}/`);
        handleJobUpdate(response.data);

        // Stop polling if job is completed
        if (['completed', 'completed_with_errors', 'failed'].includes(response.data.status)) {
          clearInterval(pollInterval);
          fetchDailyLimit();
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        clearInterval(pollInterval);
      }
    }, 3000); // Poll every 3 seconds
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Bulk Email System</h1>
          <p className="text-gray-600">Send personalized license certificates via email</p>
        </header>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">Upload Excel File</h2>
              <FileUpload 
                onFileUpload={handleFileUpload} 
                isLoading={isLoading}
                dailyLimit={dailyLimit}
              />
              
              {currentJob && (
                <div className="mt-6">
                  <button
                    onClick={startEmailSending}
                    disabled={isLoading || currentJob.status !== 'pending'}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Starting...' : 'Start Email Sending'}
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <StatusCards dailyLimit={dailyLimit} />
            
            {currentJob && (
              <ProgressTracker job={currentJob} onJobUpdate={handleJobUpdate} />
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <JobHistory />
        </div>
      </div>
    </div>
  );
}

export default App;
