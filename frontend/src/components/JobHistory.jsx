import React, { useState, useEffect, useCallback } from 'react';
import { getRecentJobs, pauseJob, resumeJob, terminateJob } from '../services/jobService';

const JobHistory = () => {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedJob, setExpandedJob] = useState(null);
  const [updatingJobId, setUpdatingJobId] = useState(null);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({
    count: 0,
    total_pages: 0,
    next: null,
    previous: null,
  });

  const fetchJobs = useCallback(async () => {
    try {
      const jobsData = await getRecentJobs({ page, pageSize: 10 });
      setJobs((jobsData.results || []).filter((job) => job.status !== 'pending'));
      setPagination({
        count: jobsData.count || 0,
        total_pages: jobsData.total_pages || 0,
        next: jobsData.next,
        previous: jobsData.previous,
      });
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setIsLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

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

  const formatDate = (dateString) => new Date(dateString).toLocaleString();

  const toggleJobExpansion = (jobId) => {
    setExpandedJob(expandedJob === jobId ? null : jobId);
  };

  const handleJobAction = async (jobId, action) => {
    setUpdatingJobId(jobId);
    try {
      const actionMap = {
        pause: pauseJob,
        resume: resumeJob,
        terminate: terminateJob,
      };
      const response = await actionMap[action](jobId);

      setJobs((prevJobs) =>
        prevJobs.map((job) =>
          job.id === jobId
            ? { ...job, status: response.data?.status || response.status || response.message || action }
            : job
        )
      );

      if (expandedJob === jobId) {
        setExpandedJob(null);
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
          <p>No started email jobs found.</p>
          <p className="text-sm">Uploaded jobs will appear here after you press Start Email Sending.</p>
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
                      <div className="text-sm font-medium">{job.total_count} emails</div>
                      <div className="text-xs text-gray-500">{formatDate(job.created_at)}</div>
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
                    {job.celery_task_id && <div>Task ID: {job.celery_task_id}</div>}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {pagination.total_pages > 1 && (
        <div className="mt-6 flex items-center justify-between border-t pt-4">
          <div className="text-sm text-gray-500">
            Page {page} of {pagination.total_pages} • {pagination.count} total jobs
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
              disabled={!pagination.previous}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Previous
            </button>
            <button
              type="button"
              onClick={() => setPage((prev) => prev + 1)}
              disabled={!pagination.next}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobHistory;
