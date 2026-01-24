# Deployment Guide

This project is configured for deployment on **Render** (Backend) and **Vercel** (Frontend), with **MongoDB Atlas** for the database.

## 1. Database Setup (MongoDB Atlas)

1.  Log in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2.  Create a new Cluster (Free Tier).
3.  In "Database Access", create a user (e.g., `admin`) and copy the password.
4.  In "Network Access", allow access from anywhere (`0.0.0.0/0`) or specific IPs.
5.  Go to "Connect" -> "Drivers" -> Copy the connection string.
    *   Format: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/crm_pro?retryWrites=true&w=majority`

## 2. Backend Deployment (Render)

1.  Push your code to GitHub.
2.  Log in to [Render](https://render.com).
3.  Click **New** -> **Web Service**.
4.  Connect your GitHub repository.
5.  Render will automatically detect the `backend/render.yaml` configuration if you point to the root, but since our backend is in a subdirectory, you might need to configure manually or set the "Root Directory" to `backend`.
    *   **Root Directory**: `backend`
    *   **Build Command**: `npm install`
    *   **Start Command**: `npm start`
6.  **Environment Variables**:
    *   `MONGO_URL`: Paste your MongoDB connection string.
    *   `JWT_SECRET`: A long random string.
    *   `FRONTEND_URL`: Your Vercel URL (add this *after* deploying frontend).
    *   `MAIL_USERNAME` & `MAIL_PASSWORD`: Your SMTP credentials (optional for simulation).
7.  Deploy. Copy the **onrender.com** URL.

## 3. Frontend Deployment (Vercel)

1.  Log in to [Vercel](https://vercel.com).
2.  **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  Configure Project:
    *   **Root Directory**: `frontend`
    *   **Framework Preset**: Create React App
5.  **Environment Variables**:
    *   `REACT_APP_API_URL`: Paste your Render Backend URL (e.g., `https://crm-backend.onrender.com`).
6.  Deploy.

## 4. Final Configuration

1.  Go back to Render Backend Dashboard.
2.  Update `FRONTEND_URL` environment variable with your new Vercel URL.
3.  Redeploy Backend.

## 5. Admin User Setup

Since registration creates an "EMPLOYEE" by default:
1.  Register a new user on the deployed site.
2.  Access your MongoDB Atlas Collections.
3.  Find the `users` collection.
4.  Edit your user document: change `role` to `ADMIN` and `status` to `ACTIVE`.
5.  Log in with your new Admin account.
