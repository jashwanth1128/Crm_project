import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_API_URL}/api`;

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Customers
  getCustomers: (params) =>
    axios.get(`${API_BASE}/customers`, { headers: getAuthHeader(), params }),
  getCustomer: (id) =>
    axios.get(`${API_BASE}/customers/${id}`, { headers: getAuthHeader() }),
  createCustomer: (data) =>
    axios.post(`${API_BASE}/customers`, data, { headers: getAuthHeader() }),
  updateCustomer: (id, data) =>
    axios.patch(`${API_BASE}/customers/${id}`, data, { headers: getAuthHeader() }),
  deleteCustomer: (id) =>
    axios.delete(`${API_BASE}/customers/${id}`, { headers: getAuthHeader() }),

  // Leads
  getLeads: (params) =>
    axios.get(`${API_BASE}/leads`, { headers: getAuthHeader(), params }),
  getLead: (id) =>
    axios.get(`${API_BASE}/leads/${id}`, { headers: getAuthHeader() }),
  createLead: (data) =>
    axios.post(`${API_BASE}/leads`, data, { headers: getAuthHeader() }),
  updateLead: (id, data) =>
    axios.patch(`${API_BASE}/leads/${id}`, data, { headers: getAuthHeader() }),
  deleteLead: (id) =>
    axios.delete(`${API_BASE}/leads/${id}`, { headers: getAuthHeader() }),
  getLeadStats: () =>
    axios.get(`${API_BASE}/leads/stats/overview`, { headers: getAuthHeader() }),

  // Activities
  getActivities: (params) =>
    axios.get(`${API_BASE}/activities`, { headers: getAuthHeader(), params }),
  createActivity: (data) =>
    axios.post(`${API_BASE}/activities`, data, { headers: getAuthHeader() }),

  // Notifications
  getNotifications: (params) =>
    axios.get(`${API_BASE}/notifications`, { headers: getAuthHeader(), params }),
  markNotificationRead: (id) =>
    axios.patch(`${API_BASE}/notifications/${id}/read`, {}, { headers: getAuthHeader() }),
  markAllNotificationsRead: () =>
    axios.post(`${API_BASE}/notifications/read-all`, {}, { headers: getAuthHeader() }),

  // Users
  getUsers: () =>
    axios.get(`${API_BASE}/users`, { headers: getAuthHeader() }),
  updateUser: (id, data) =>
    axios.patch(`${API_BASE}/users/${id}`, data, { headers: getAuthHeader() }),

  // Audit Logs
  getAuditLogs: (params) =>
    axios.get(`${API_BASE}/audit-logs`, { headers: getAuthHeader(), params }),
};
