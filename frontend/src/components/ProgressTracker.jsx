import React, { useState } from 'react';
import { pauseJob, resumeJob, terminateJob } from '../services/jobService';

const ProgressTracker = ({ job, onJobUpdate }) => {
  const [isUpdating, setIsUpdating] = useState(false);

  if (!job) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Live Email Delivery</h3>
        <p className="text-gray-500">No job data available</p>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'paused':
        return 'bg-orange-100 text-orange-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressColor = () => {
    if (job.status === 'failed') return 'bg-red-500';
    if (job.status === 'completed') return 'bg-green-500';
    if (job.status === 'terminated') return 'bg-gray-500';
    if (job.status === 'paused') return 'bg-orange-500';
    return 'bg-blue-500';
  };

  const handlePause = async () => {
    setIsUpdating(true);
    try {
      await pauseJob(job.id);
      onJobUpdate?.({ ...job, status: 'paused' });
    } catch (error) {
      console.error('Error pausing job:', error);
      alert(error.response?.data?.error || 'Error pausing job');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleResume = async () => {
    setIsUpdating(true);
    try {
      await resumeJob(job.id);
      onJobUpdate?.({ ...job, status: 'processing' });
    } catch (error) {
      console.error('Error resuming job:', error);
      alert(error.response?.data?.error || 'Error resuming job');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleTerminate = async () => {
    if (!window.confirm('Are you sure you want to terminate this email sending job? This action cannot be undone.')) {
      return;
    }

    setIsUpdating(true);
    try {
      await terminateJob(job.id);
      onJobUpdate?.({ ...job, status: 'terminated' });
    } catch (error) {
      console.error('Error terminating job:', error);
      alert(error.response?.data?.error || 'Error terminating job');
    } finally {
      setIsUpdating(false);
    }
  };

  const renderControlButtons = () => {
    if (job.status === 'processing') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={handlePause}
            disabled={isUpdating}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
          >
            {isUpdating ? 'Pausing...' : 'Pause'}
          </button>
          <button
            onClick={handleTerminate}
            disabled={isUpdating}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
          >
            {isUpdating ? 'Terminating...' : 'Terminate'}
          </button>
        </div>
      );
    }

    if (job.status === 'paused') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={handleResume}
            disabled={isUpdating}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
          >
            {isUpdating ? 'Resuming...' : 'Resume'}
          </button>
          <button
            onClick={handleTerminate}
            disabled={isUpdating}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
          >
            {isUpdating ? 'Terminating...' : 'Terminate'}
          </button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Live Email Delivery</h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Status:</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status || 'pending')}`}>
            {job.status ? job.status.charAt(0).toUpperCase() + job.status.slice(1) : 'Pending'}
          </span>
        </div>

        <div>
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round(job.progress_percentage || 0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`${getProgressColor()} h-2 rounded-full transition-all duration-300`}
              style={{ width: `${job.progress_percentage || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-gray-800">{job.total_count || 0}</div>
            <div className="text-xs text-gray-600">Total Emails</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded">
            <div className="text-2xl font-bold text-green-600">{job.sent_count || 0}</div>
            <div className="text-xs text-gray-600">Sent</div>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded">
            <div className="text-2xl font-bold text-yellow-600">{job.pending_count || 0}</div>
            <div className="text-xs text-gray-600">Pending</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded">
            <div className="text-2xl font-bold text-red-600">{job.failed_count || 0}</div>
            <div className="text-xs text-gray-600">Failed</div>
          </div>
        </div>

        {job.failed_records && job.failed_records.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-red-700 mb-2">Failed Emails:</h4>
            <div className="max-h-32 overflow-y-auto bg-red-50 rounded p-2">
              {job.failed_records.map((record, index) => (
                <div key={index} className="text-xs text-red-600 mb-1">
                  <strong>{record.name}</strong> ({record.email})
                  {record.error_message && <div className="text-xs text-red-500 ml-2">{record.error_message}</div>}
                </div>
              ))}
            </div>
          </div>
        )}

        {renderControlButtons()}

        <div className="text-xs text-gray-500 border-t pt-2">
          Job ID: {job.id}
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;
