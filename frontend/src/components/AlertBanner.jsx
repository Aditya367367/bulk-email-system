import React from 'react';

const AlertBanner = ({ type = 'success', message }) => {
  if (!message) {
    return null;
  }

  const styles = {
    success: 'bg-green-100 border-green-400 text-green-700',
    error: 'bg-red-100 border-red-400 text-red-700',
  };

  return (
    <div className={`mb-4 rounded border px-4 py-3 ${styles[type] || styles.success}`}>
      {message}
    </div>
  );
};

export default AlertBanner;
