import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../utils/api';
import toast from 'react-hot-toast';
import { FiMail, FiLock, FiArrowRight } from 'react-icons/fi';

const ForgotPasswordPage = () => {
    const [step, setStep] = useState(1); // 1: Email, 2: New Password
    const [email, setEmail] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSendReset = async (e) => {
        e.preventDefault();
        if (!email) return toast.error('Please enter your email address');

        setLoading(true);
        try {
            await authAPI.forgotPassword({ email });
            toast.success('If an account exists, a reset email has been sent!');
            setStep(2);
        } catch (error) {
            // Always show a generic success to avoid email enumeration
            toast.success('If an account exists, a reset email has been sent!');
            setStep(2);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card" style={{ maxWidth: '420px' }}>
                <div style={{ textAlign: 'center', marginBottom: '28px' }}>
                    <div style={{
                        width: 56, height: 56, borderRadius: '14px',
                        background: 'linear-gradient(135deg, #ff9900, #e68a00)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        margin: '0 auto 16px', fontSize: '1.6rem',
                        boxShadow: '0 4px 16px rgba(255,153,0,0.3)'
                    }}>
                        🔑
                    </div>
                    <h2>Forgot Password</h2>
                    <p className="auth-subtitle">Enter your registered email to reset your password</p>
                </div>

                {step === 1 ? (
                    <form onSubmit={handleSendReset}>
                        <div className="form-group">
                            <label className="form-label"><FiMail size={13} /> Email Address</label>
                            <input
                                className="form-input"
                                type="email"
                                placeholder="you@example.com"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                required
                                autoFocus
                            />
                        </div>
                        <button className="btn btn-primary btn-full btn-lg" type="submit" disabled={loading} style={{ marginTop: '16px' }}>
                            {loading ? 'Sending...' : <><span>Send Reset Link</span> <FiArrowRight size={16} /></>}
                        </button>
                    </form>
                ) : (
                    <div style={{ textAlign: 'center', padding: '16px 0' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📧</div>
                        <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                            Check your inbox at <strong>{email}</strong> for a password reset link.
                        </p>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '12px' }}>
                            Didn't receive it? Check your spam folder or{' '}
                            <button
                                onClick={() => setStep(1)}
                                style={{ background: 'none', border: 'none', color: '#ff9900', cursor: 'pointer', fontWeight: 600, fontSize: 'inherit' }}
                            >
                                try again
                            </button>
                        </p>
                    </div>
                )}

                <p className="auth-footer" style={{ marginTop: '24px' }}>
                    <Link to="/login">Back to Login</Link>
                </p>
            </div>
        </div>
    );
};

export default ForgotPasswordPage;
