import React from 'react';

const StatusCards = ({ dailyLimit }) => {
  const getRemainingColor = () => {
    const percentage = (dailyLimit.remaining_emails / 100) * 100;
    if (percentage <= 20) return 'text-red-600';
    if (percentage <= 50) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getProgressColor = () => {
    const percentage = (dailyLimit.emails_sent / 100) * 100;
    if (percentage >= 80) return 'bg-red-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Daily Email Limit</h3>

        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Today's Usage</span>
            <span className="text-sm font-medium">
              {dailyLimit.emails_sent} / {dailyLimit.emails_sent + dailyLimit.remaining_emails}
            </span>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`${getProgressColor()} h-2 rounded-full transition-all duration-300`}
              style={{ width: `${(dailyLimit.emails_sent / 100) * 100}%` }}
            ></div>
          </div>

          <div className="text-center">
            <div className={`text-3xl font-bold ${getRemainingColor()}`}>
              {dailyLimit.remaining_emails}
            </div>
            <div className="text-xs text-gray-600">Remaining Emails</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>

        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
            <span className="text-sm text-blue-800">Daily Limit</span>
            <span className="text-sm font-bold text-blue-800">100</span>
          </div>

          <div className="flex justify-between items-center p-3 bg-green-50 rounded">
            <span className="text-sm text-green-800">Sent Today</span>
            <span className="text-sm font-bold text-green-800">{dailyLimit.emails_sent}</span>
          </div>

          <div className="flex justify-between items-center p-3 bg-yellow-50 rounded">
            <span className="text-sm text-yellow-800">Available</span>
            <span className="text-sm font-bold text-yellow-800">{dailyLimit.remaining_emails}</span>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-800 mb-2">Tips:</h4>
        <ul className="text-xs text-blue-700 space-y-1">
          <li>Excel files must contain 6 required columns: ref_no, name, email, company_name, address_line1, address_line2</li>
          <li>Maximum 100 rows per file</li>
          <li>After upload, click Start Email Sending to process the bulk email job</li>
          <li>Each email includes an HTML message and the generated PDF attachment</li>
          <li>Emails are sent with 7-second delays</li>
          <li>Check failed logs for troubleshooting</li>
        </ul>
      </div>
    </div>
  );
};

export default StatusCards;
