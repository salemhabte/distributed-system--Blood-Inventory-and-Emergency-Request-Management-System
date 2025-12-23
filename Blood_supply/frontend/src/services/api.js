import axios from 'axios';

const AUTH_URL = 'http://localhost:8003/api/auth';
const BLOOD_BANK_URL = 'http://localhost:8001/api/v1/blood-bank';
const HOSPITAL_URL = 'http://localhost:8000/api/v1/hospital';

const api = axios.create({
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: (credentials) => axios.post(`${AUTH_URL}/login/`, credentials),
  register: (userData) => axios.post(`${AUTH_URL}/register/`, userData),
  getProfile: () => api.get(`${AUTH_URL}/profile/`),
};

export const bloodBankService = {
  getInventory: () => api.get(`${BLOOD_BANK_URL}/inventory/`),
  addBatch: (batchData) => api.post(`${BLOOD_BANK_URL}/inventory/`, batchData),
};

export const hospitalService = {
  createPatient: (patientData) => api.post(`${HOSPITAL_URL}/patients`, patientData).catch(err => {
    console.error("Patient Creation Error:", err.response?.data || err.message);
    throw err;
  }),
  getPatients: () => api.get(`${HOSPITAL_URL}/patients`),
  createRequest: (requestData) => api.post(`${HOSPITAL_URL}/blood-requests`, requestData).catch(err => {
    console.error("Blood Request Error:", err.response?.data || err.message);
    throw err;
  }),
  getRequests: () => api.get(`${HOSPITAL_URL}/blood-requests`),
};

export default api;
