import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const JobHistory = () => {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedJob, setExpandedJob] = useState(null);
  const [updatingJobId, setUpdatingJobId] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs/`);
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setIsLoading(false);
    }
  };

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
      case 'completed_with_errors':
        return 'bg-orange-100 text-orange-800';
      case 'paused':
        return 'bg-purple-100 text-purple-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const toggleJobExpansion = (jobId) => {
    setExpandedJob(expandedJob === jobId ? null : jobId);
  };

  const handleJobAction = async (jobId, action) => {
    setUpdatingJobId(jobId);
    try {
      const response = await axios.post(`${API_BASE_URL}/${action}/${jobId}/`);
      
      // Update the job in the list
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, status: response.data.status }
            : job
        )
      );
      
      // If this job is expanded, update it too
      if (expandedJob === jobId) {
        setExpandedJob(null); // Collapse and re-expand to refresh
        setTimeout(() => setExpandedJob(jobId), 100);
      }
    } catch (error) {
      console.error(`Error ${action}ing job:`, error);
      alert(error.response?.data?.error || `Error ${action}ing job`);
    } finally {
      setUpdatingJobId(null);
    }
  };

  const renderJobControls = (job) => {
    if (job.status === 'processing') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={() => handleJobAction(job.id, 'pause')}
            disabled={updatingJobId === job.id}
            className="px-3 py-1 bg-orange-600 text-white rounded text-xs hover:bg-orange-700 disabled:bg-gray-400"
          >
            {updatingJobId === job.id ? 'Pausing...' : 'Pause'}
          </button>
          <button
            onClick={() => handleJobAction(job.id, 'terminate')}
            disabled={updatingJobId === job.id}
            className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 disabled:bg-gray-400"
          >
            {updatingJobId === job.id ? 'Terminating...' : 'Terminate'}
          </button>
        </div>
      );
    }
    
    if (job.status === 'pending') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={() => handleJobAction(job.id, 'terminate')}
            disabled={updatingJobId === job.id}
            className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 disabled:bg-gray-400"
          >
            {updatingJobId === job.id ? 'Terminating...' : 'Terminate'}
          </button>
        </div>
      );
    }
    
    if (job.status === 'paused') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={() => handleJobAction(job.id, 'resume')}
            disabled={updatingJobId === job.id}
            className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 disabled:bg-gray-400"
          >
            {updatingJobId === job.id ? 'Resuming...' : 'Resume'}
          </button>
          <button
            onClick={() => handleJobAction(job.id, 'terminate')}
            disabled={updatingJobId === job.id}
            className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 disabled:bg-gray-400"
          >
            {updatingJobId === job.id ? 'Terminating...' : 'Terminate'}
          </button>
        </div>
      );
    }
    
    return null;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Recent Email Jobs</h2>
      
      {jobs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No email jobs found.</p>
          <p className="text-sm">Upload an Excel file to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="border rounded-lg overflow-hidden">
              <div 
                className="p-4 bg-white hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => toggleJobExpansion(job.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1).replace('_', ' ')}
                    </span>
                    <div>
                      <div className="text-sm font-medium">
                        {job.total_count} emails
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDate(job.created_at)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right text-sm">
                      <div className="text-green-600 font-medium">{job.sent_count} sent</div>
                      <div className="text-red-600">{job.failed_count} failed</div>
                    </div>
                    
                    {renderJobControls(job)}
                    
                    <svg 
                      className={`w-5 h-5 text-gray-400 transition-transform ${expandedJob === job.id ? 'rotate-180' : ''}`}
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${
                        job.status === 'failed' ? 'bg-red-500' : 
                        job.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${job.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              {/* Expanded Details */}
              {expandedJob === job.id && (
                <div className="border-t bg-gray-50 p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-800">{job.total_count}</div>
                      <div className="text-xs text-gray-600">Total</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-green-600">{job.sent_count}</div>
                      <div className="text-xs text-gray-600">Sent</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-yellow-600">{job.pending_count}</div>
                      <div className="text-xs text-gray-600">Pending</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-red-600">{job.failed_count}</div>
                      <div className="text-xs text-gray-600">Failed</div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500 space-y-1">
                    <div>Job ID: {job.id}</div>
                    <div>Created: {formatDate(job.created_at)}</div>
                    <div>Updated: {formatDate(job.updated_at)}</div>
                    {job.celery_task_id && (
                      <div>Task ID: {job.celery_task_id}</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JobHistory;
