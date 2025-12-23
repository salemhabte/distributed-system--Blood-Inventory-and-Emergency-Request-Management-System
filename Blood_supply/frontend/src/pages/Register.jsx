import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/api';
import { UserPlus, User, Mail, Lock, Phone, MapPin, Building, ShieldCheck } from 'lucide-react';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'hospital',
    organization_name: '',
    phone_number: '',
    address: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.password_confirm) {
        setError('Passwords do not match');
        return;
    }

    setLoading(true);
    try {
      await authService.register({
        ...formData,
        role: formData.role // Ensure we send the correct role value
      });
      alert('Registration successful! Please login.');
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Try different username/email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in" style={{ display: 'flex', width: '100%', minHeight: '90vh', alignItems: 'center', justifyContent: 'center', padding: '2rem 0' }}>
      <div className="card" style={{ maxWidth: '640px', width: '100%' }}>
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
            <UserPlus size={32} />
          </div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Join the Network</h2>
          <p style={{ color: 'var(--text-dim)' }}>Register your organization to start saving lives</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="input-group">
                <label className="label">Username</label>
                <div style={{ position: 'relative' }}>
                  <User size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input type="text" name="username" className="input" style={{ paddingLeft: '2.5rem' }} onChange={handleChange} required />
                </div>
            </div>
            <div className="input-group">
                <label className="label">Email Address</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input type="email" name="email" className="input" style={{ paddingLeft: '2.5rem' }} onChange={handleChange} required />
                </div>
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="input-group">
                <label className="label">Password</label>
                <input type="password" name="password" className="input" onChange={handleChange} required />
            </div>
            <div className="input-group">
                <label className="label">Confirm Password</label>
                <input type="password" name="password_confirm" className="input" onChange={handleChange} required />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="input-group">
                <label className="label">First Name</label>
                <input type="text" name="first_name" className="input" onChange={handleChange} required />
            </div>
            <div className="input-group">
                <label className="label">Last Name</label>
                <input type="text" name="last_name" className="input" onChange={handleChange} required />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
            <div className="input-group">
                <label className="label">Organization Name</label>
                <div style={{ position: 'relative' }}>
                  <Building size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input type="text" name="organization_name" className="input" style={{ paddingLeft: '2.5rem' }} onChange={handleChange} required />
                </div>
            </div>
            <div className="input-group">
                <label className="label">Account Role</label>
                <div style={{ position: 'relative' }}>
                  <ShieldCheck size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <select name="role" className="input" style={{ paddingLeft: '2.5rem' }} onChange={handleChange}>
                      <option value="hospital">Hospital</option>
                      <option value="blood_bank">Blood Bank</option>
                  </select>
                </div>
            </div>
          </div>

          <div className="input-group">
              <label className="label">Phone Number</label>
              <div style={{ position: 'relative' }}>
                <Phone size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input type="text" name="phone_number" className="input" style={{ paddingLeft: '2.5rem' }} onChange={handleChange} required />
              </div>
          </div>

          <div className="input-group">
              <label className="label">Full Address</label>
              <div style={{ position: 'relative' }}>
                <MapPin size={16} style={{ position: 'absolute', left: '1rem', top: '0.875rem', color: 'var(--text-muted)' }} />
                <textarea name="address" className="input" style={{ paddingLeft: '2.5rem', minHeight: '80px' }} onChange={handleChange} required />
              </div>
          </div>

          {error && <div className="error" style={{ marginBottom: '1.5rem' }}>{error}</div>}
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Processing...' : 'Create Account'}
          </button>
        </form>
        <div style={{ textAlign: 'center', marginTop: '2rem', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
          Already registered? <Link to="/login" style={{ color: 'var(--primary)', fontWeight: '600', textDecoration: 'none' }}>Log in here</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
