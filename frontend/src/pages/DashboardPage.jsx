import React, { useEffect, useState } from 'react';
import FileUpload from '../components/FileUpload.jsx';
import ProgressTracker from '../components/ProgressTracker.jsx';
import StatusCards from '../components/StatusCards.jsx';
import JobHistory from '../components/JobHistory.jsx';
import ReadyToStartCard from '../components/ReadyToStartCard';
import AlertBanner from '../components/AlertBanner';
import {
  getDailyLimit,
  getJobStatus,
  getRecentJobs,
  startEmailJob,
  uploadExcelFile,
} from '../services/jobService';

const DashboardPage = () => {
  const [currentJob, setCurrentJob] = useState(null);
  const [dailyLimit, setDailyLimit] = useState({ emails_sent: 0, remaining_emails: 100 });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchDailyLimitInfo();
    fetchJobHistory();
  }, []);

  const getJobId = (job) => job?.id || job?.job_id;
  const isCurrentJobPending = currentJob?.status === 'pending';
  const isCurrentJobStarted = currentJob && currentJob.status && currentJob.status !== 'pending';

  const fetchDailyLimitInfo = async () => {
    try {
      const data = await getDailyLimit();
      setDailyLimit(data);
    } catch (err) {
      console.error('Error fetching daily limit:', err);
    }
  };

  const fetchJobHistory = async () => {
    try {
      await getRecentJobs();
    } catch (err) {
      console.error('Error fetching job history:', err);
    }
  };

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await uploadExcelFile(file);
      setCurrentJob(data);
      setSuccess('Excel file uploaded successfully. Click "Start Email Sending" to begin the bulk email job.');
      fetchDailyLimitInfo();
    } catch (err) {
      setError(err.response?.data?.error || 'Error uploading file');
    } finally {
      setIsLoading(false);
    }
  };

  const startEmailSending = async () => {
    if (!currentJob) return;

    const jobId = getJobId(currentJob);
    if (!jobId) {
      setError('Uploaded job ID is missing. Please upload the Excel file again.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const data = await startEmailJob(jobId);
      setCurrentJob((prev) => ({ ...prev, ...data }));
      setSuccess('Email sending started. The system will generate the PDF, attach it to an HTML email, and send messages with a 7-second delay.');
      pollJobStatus(jobId);
    } catch (err) {
      setError(err.response?.data?.error || 'Error starting email sending');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJobUpdate = (updatedJob) => {
    setCurrentJob((prev) => ({ ...prev, ...updatedJob }));
  };

  const pollJobStatus = async (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const data = await getJobStatus(jobId);
        handleJobUpdate(data);

        if (['completed', 'completed_with_errors', 'failed'].includes(data.status)) {
          clearInterval(pollInterval);
          fetchDailyLimitInfo();
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        clearInterval(pollInterval);
      }
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 text-center">
          <h1 className="mb-2 text-4xl font-bold text-gray-800">Bulk Email System</h1>
          <p className="text-gray-600">Upload Excel data, review the draft job, then start responsive bulk email delivery with PDF attachments</p>
          
        </header>

        <AlertBanner type="error" message={error} />
        <AlertBanner type="success" message={success} />

        <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="rounded-lg bg-white p-6 shadow-md">
              <h2 className="mb-4 text-2xl font-semibold">Upload Excel File</h2>
              <FileUpload
                onFileUpload={handleFileUpload}
                isLoading={isLoading}
                dailyLimit={dailyLimit}
              />

              {currentJob && isCurrentJobPending && (
                <ReadyToStartCard
                  currentJob={currentJob}
                  isLoading={isLoading}
                  onStart={startEmailSending}
                />
              )}

              {currentJob && isCurrentJobStarted && (
                <div className="mt-6">
                  <button
                    type="button"
                    disabled
                    className="rounded-lg bg-blue-600 px-6 py-2 text-white disabled:cursor-not-allowed disabled:bg-gray-400"
                  >
                    Email Job In Progress
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <StatusCards dailyLimit={dailyLimit} />

            {isCurrentJobStarted && (
              <ProgressTracker job={currentJob} onJobUpdate={handleJobUpdate} />
            )}
          </div>
        </div>

        <div className="rounded-lg bg-white p-6 shadow-md">
          <JobHistory />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
