# CRM Project

A full-stack Customer Relationship Management (CRM) application with a modern React frontend and a robust Node.js/Express backend.

## Features

-   **Dashboard**: Overview of sales performance and recent activities.
-   **Deal Management**: Kanban board to track leaks and deals through stages.
-   **Customer Management**: Manage customer details and history.
-   **Authentication**: Secure JWT-based auth with Role-Based Access Control (RBAC).
-   **Real-time Updates**: Socket.io integration for instant updates on team actions.
-   **Audit Logs**: Track important system changes.

## Tech Stack

-   **Frontend**: React, Tailwind CSS, Radix UI, Axios, React Router.
-   **Backend**: Node.js, Express, MongoDB (Mongoose), Socket.io, Nodemailer.
-   **Deployment**: Render (Backend), Vercel (Frontend), MongoDB Atlas (Database).

## Project Structure

-   `backend/`: Node.js Express API.
-   `frontend/`: React Application.
-   `backend_legacy/`: Archive of previous Python implementation.

## Local Setup

### Backend

1.  Navigate to backend: `cd backend`
2.  Install dependencies: `npm install`
3.  Create `.env` file (copy from sample):
    ```
    PORT=8000
    MONGO_URL=mongodb+srv://...
    JWT_SECRET=dev_secret
    FRONTEND_URL=http://localhost:3000
    ```
4.  Start server: `npm run dev`

### Frontend

1.  Navigate to frontend: `cd frontend`
2.  Install dependencies: `npm install`
3.  Create `.env` file:
    ```
    REACT_APP_API_URL=http://localhost:8000
    ```
4.  Start app: `npm start`

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed step-by-step instructions.

## API Documentation

The backend exposes RESTful endpoints at `/api`.

-   `/api/auth`: Register, Login, Me.
-   `/api/customers`: CRUD for customers.
-   `/api/leads`: CRUD for leads/deals.
-   `/api/activities`: CRUD for activities.
-   `/api/notifications`: Get/Mark Read notifications.
