import React from 'react';

const ReadyToStartCard = ({ currentJob, isLoading, onStart }) => {
  if (!currentJob) {
    return null;
  }

  return (
    <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-5">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Ready To Start</p>
          <h3 className="mt-1 text-xl font-semibold text-gray-900">Excel uploaded successfully</h3>
          <p className="mt-1 text-sm text-gray-600">
            {currentJob.total_count} email{currentJob.total_count === 1 ? '' : 's'} prepared. This job will stay here until you press Start.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm md:min-w-[240px]">
          <div className="rounded-lg bg-white p-3 text-center shadow-sm">
            <div className="text-lg font-bold text-gray-900">{currentJob.total_count || 0}</div>
            <div className="text-xs text-gray-500">Queued Emails</div>
          </div>
          <div className="rounded-lg bg-white p-3 text-center shadow-sm">
            <div className="text-lg font-bold text-yellow-600">{currentJob.pending_count || 0}</div>
            <div className="text-xs text-gray-500">Pending Start</div>
          </div>
        </div>
      </div>

      <div className="mt-5">
        <button
          onClick={onStart}
          disabled={isLoading}
          className="inline-flex items-center rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {isLoading ? 'Starting...' : 'Start Email Sending'}
        </button>
      </div>
    </div>
  );
};

export default ReadyToStartCard;
