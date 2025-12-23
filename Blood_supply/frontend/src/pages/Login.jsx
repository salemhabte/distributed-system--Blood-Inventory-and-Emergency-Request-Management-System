import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, User, Lock, AlertCircle } from 'lucide-react';

const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(credentials);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in" style={{ display: 'flex', width: '100%', minHeight: '80vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="card" style={{ maxWidth: '420px', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <div style={{ 
            width: '64px', 
            height: '64px', 
            background: 'var(--primary-glow)', 
            borderRadius: '1rem', 
            display: 'inline-flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: 'var(--primary)',
            marginBottom: '1rem'
          }}>
            <LogIn size={32} />
          </div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Welcome Back</h2>
          <p style={{ color: 'var(--text-dim)' }}>Access the blood management gateway</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="label">Username</label>
            <div style={{ position: 'relative' }}>
              <User size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
              <input
                type="text"
                name="username"
                className="input"
                style={{ paddingLeft: '3rem' }}
                value={credentials.username}
                onChange={handleChange}
                required
                placeholder="Enter username"
              />
            </div>
          </div>

          <div className="input-group" style={{ marginBottom: '2rem' }}>
            <label className="label">Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
              <input
                type="password"
                name="password"
                className="input"
                style={{ paddingLeft: '3rem' }}
                value={credentials.password}
                onChange={handleChange}
                required
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="error" style={{ marginBottom: '1.5rem', background: 'rgba(239, 71, 111, 0.1)', padding: '0.75rem', borderRadius: '0.5rem' }}>
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '2rem', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
          New to BloodLink? <Link to="/register" style={{ color: 'var(--primary)', fontWeight: '600', textDecoration: 'none' }}>Initialize account</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
