import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const VerifyEmailPage = () => {
    const [otp, setOtp] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const email = location.state?.email;

    const handleVerify = async (e) => {
        e.preventDefault();
        if (!otp) return;
        setLoading(true);
        try {
            const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const response = await axios.post(`${API_URL}/api/auth/verify-email`, {
                email,
                otp
            });
            // If verification returns a token, we could login immediately, 
            // but for now let's redirect to login for simplicity or dashboard if we save token.
            // Let's assume the backend returns the token like login.
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                // Force a reload or update context (simplified here)
                window.location.href = '/dashboard';
            } else {
                toast.success('Email verified! Please login.');
                navigate('/login');
            }
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Verification failed');
        } finally {
            setLoading(false);
        }
    };

    if (!email) {
        return <div className="p-8 text-center">No email provided. Please register first.</div>;
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <div className="w-full max-w-md space-y-8 bg-card p-8 rounded-lg border shadow-sm">
                <div className="text-center">
                    <h2 className="text-2xl font-bold">Verify Your Email</h2>
                    <p className="text-muted-foreground mt-2">
                        Enter the code sent to {email}
                    </p>
                </div>
                <form onSubmit={handleVerify} className="space-y-6">
                    <div>
                        <input
                            type="text"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            placeholder="Enter 6-digit code"
                            className="w-full p-3 rounded-md border bg-background text-foreground text-center text-2xl tracking-widest"
                            maxLength={6}
                        />
                    </div>
                    <Button className="w-full" type="submit" disabled={loading}>
                        {loading ? 'Verifying...' : 'Verify Email'}
                    </Button>
                </form>
            </div>
        </div>
    );
};

export default VerifyEmailPage;
