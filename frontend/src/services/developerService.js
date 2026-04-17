import api from './api';

export const getDeveloperInfo = async () => {
  const response = await api.get('/developer-info/');
  return response.data;
};
