import api from './api';

export const uploadExcelFile = async (file) => {
  const formData = new FormData();
  formData.append('excel_file', file);

  const response = await api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const startEmailJob = async (jobId) => {
  const response = await api.post(`/start/${jobId}/`);
  return response.data;
};

export const getDailyLimit = async () => {
  const response = await api.get('/daily-limit/');
  return response.data;
};

export const getRecentJobs = async ({ page = 1, pageSize = 10 } = {}) => {
  const response = await api.get('/jobs/', {
    params: {
      page,
      page_size: pageSize,
    },
  });
  return response.data;
};

export const getJobStatus = async (jobId) => {
  const response = await api.get(`/status/${jobId}/`);
  return response.data;
};

export const pauseJob = async (jobId) => {
  const response = await api.post(`/pause/${jobId}/`);
  return response.data;
};

export const resumeJob = async (jobId) => {
  const response = await api.post(`/resume/${jobId}/`);
  return response.data;
};

export const terminateJob = async (jobId) => {
  const response = await api.post(`/terminate/${jobId}/`);
  return response.data;
};
