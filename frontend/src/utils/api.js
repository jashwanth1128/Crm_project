import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_API_URL}/api`;

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Accounts (mapped to Customers)
  getAccounts: (params) =>
    axios.get(`${API_BASE}/customers`, { headers: getAuthHeader(), params }),
  getAccount: (id) =>
    axios.get(`${API_BASE}/customers/${id}`, { headers: getAuthHeader() }),
  createAccount: (data) =>
    axios.post(`${API_BASE}/customers`, data, { headers: getAuthHeader() }),
  updateAccount: (id, data) =>
    axios.patch(`${API_BASE}/customers/${id}`, data, { headers: getAuthHeader() }),
  deleteAccount: (id) =>
    axios.delete(`${API_BASE}/customers/${id}`, { headers: getAuthHeader() }),

  // Contacts (mapped to Customers for now as they are similar entities in this simple CRM)
  getContacts: (params) =>
    axios.get(`${API_BASE}/customers`, { headers: getAuthHeader(), params }),
  getContact: (id) =>
    axios.get(`${API_BASE}/customers/${id}`, { headers: getAuthHeader() }),
  createContact: (data) =>
    axios.post(`${API_BASE}/customers`, data, { headers: getAuthHeader() }),
  updateContact: (id, data) =>
    axios.patch(`${API_BASE}/customers/${id}`, data, { headers: getAuthHeader() }),
  deleteContact: (id) =>
    axios.delete(`${API_BASE}/customers/${id}`, { headers: getAuthHeader() }),

  // Deals (mapped to Leads)
  getDeals: (params) =>
    axios.get(`${API_BASE}/leads`, { headers: getAuthHeader(), params }),
  getDeal: (id) =>
    axios.get(`${API_BASE}/leads/${id}`, { headers: getAuthHeader() }),
  createDeal: (data) =>
    axios.post(`${API_BASE}/leads`, data, { headers: getAuthHeader() }),
  updateDeal: (id, data) =>
    axios.patch(`${API_BASE}/leads/${id}`, data, { headers: getAuthHeader() }),
  deleteDeal: (id) =>
    axios.delete(`${API_BASE}/leads/${id}`, { headers: getAuthHeader() }),

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
  // Updated Convert Endpoint to just patch status
  convertLead: (id) =>
    axios.patch(`${API_BASE}/leads/${id}`, { status: 'CONVERTED' }, { headers: getAuthHeader() }),

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
    axios.get(`${API_BASE}/admin/audit-logs`, { headers: getAuthHeader(), params }),
};
