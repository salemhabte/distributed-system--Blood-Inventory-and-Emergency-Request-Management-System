import React, { useState, useEffect } from 'react';
import { hospitalService } from '../services/api';
import { 
  Users, FileText, Send, Plus, Activity, Clock, 
  AlertCircle, Shield, Briefcase, ChevronRight, 
  Search, Filter, MoreHorizontal, UserCheck
} from 'lucide-react';

const HospitalDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('requests');
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const [newPatient, setNewPatient] = useState({
    first_name: '', last_name: '', age: 30, blood_type: 'A+', diagnosis: ''
  });

  const [newRequest, setNewRequest] = useState({
    patient: '', blood_type: 'A+', units_required: 1, priority: 'NORMAL', notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [respPatients, respRequests] = await Promise.all([
        hospitalService.getPatients(),
        hospitalService.getRequests()
      ]);
      setPatients(respPatients.data);
      setRequests(respRequests.data);
    } catch (err) {
      console.error('Failed to fetch hospital data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPatient = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      await hospitalService.createPatient(newPatient);
      setShowPatientModal(false);
      fetchData();
    } catch (err) {
      const msg = err.response?.data 
        ? Object.entries(err.response.data).map(([k, v]) => `${k}: ${v}`).join(', ')
        : 'Failed to create patient record. Please check your connection.';
      setErrorMsg(msg);
    }
  };

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      await hospitalService.createRequest(newRequest);
      setShowRequestModal(false);
      fetchData();
    } catch (err) {
      const msg = err.response?.data 
        ? Object.entries(err.response.data).map(([k, v]) => `${k}: ${v}`).join(', ')
        : 'Failed to submit blood request.';
      setErrorMsg(msg);
    }
  };

  return (
    <div className="fade-in hospital-portal" style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem', height: 'calc(100vh - 120px)' }}>
      {/* Secondary Sidebar */}
      <aside className="glass" style={{ borderRadius: '1.5rem', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ padding: '0 0.5rem 1.5rem 0.5rem', borderBottom: '1px solid var(--glass-border)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'white' }}>Hospital Command</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Central Medical Operations</p>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button 
            onClick={() => setActiveTab('requests')}
            className={`nav-item ${activeTab === 'requests' ? 'active' : ''}`}
            style={navItemStyle(activeTab === 'requests')}
          >
            <Activity size={20} />
            <span>Blood Requests</span>
            {requests.length > 0 && <span className="nav-badge">{requests.length}</span>}
          </button>
          <button 
            onClick={() => setActiveTab('patients')}
            className={`nav-item ${activeTab === 'patients' ? 'active' : ''}`}
            style={navItemStyle(activeTab === 'patients')}
          >
            <Users size={20} />
            <span>Patient Registry</span>
          </button>
        </nav>

        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => setShowRequestModal(true)}>
            <Send size={18} /> New Request
          </button>
          <button className="btn btn-secondary" style={{ width: '100%', background: 'rgba(255,255,255,0.05)' }} onClick={() => setShowPatientModal(true)}>
            <Plus size={18} /> Add Patient
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <section style={{ overflowY: 'auto', paddingRight: '1rem' }}>
        <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>{activeTab === 'requests' ? 'Dispatch Monitor' : 'Medical Records'}</h1>
            <p style={{ color: 'var(--text-dim)' }}>
              {activeTab === 'requests' ? 'Real-time tracking of blood inventory requests' : 'Manage your hospital patient population'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
             <div className="glass" style={{ padding: '0.5rem 1rem', borderRadius: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Search size={16} color="var(--text-muted)" />
                <input type="text" placeholder="Search..." style={{ background: 'none', border: 'none', outline: 'none', color: 'white', fontSize: '0.9rem' }} />
             </div>
          </div>
        </header>

        {activeTab === 'requests' ? (
          <div className="table-container fade-in">
             <table>
               <thead>
                 <tr>
                   <th>TRACE ID</th>
                   <th>BLOOD TYPE</th>
                   <th>UNITS</th>
                   <th>PRIORITY</th>
                   <th>STATUS</th>
                   <th>SUBMITTED</th>
                 </tr>
               </thead>
               <tbody>
                 {requests.map((req) => (
                   <tr key={req.request_id}>
                     <td style={{ fontFamily: 'monospace', color: 'var(--primary)', fontWeight: 600 }}>#{req.request_id.substring(0, 8)}</td>
                     <td>
                      <div className="blood-chip">
                        <Droplet size={14} />
                        {req.blood_type}
                      </div>
                     </td>
                     <td style={{ fontWeight: 700 }}>{req.units_required}</td>
                     <td>
                      <span className={`badge ${req.priority === 'EMERGENCY' ? 'badge-danger' : 'badge-primary'}`}>
                        {req.priority}
                      </span>
                     </td>
                     <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: getStatusColor(req.status), boxShadow: `0 0 8px ${getStatusColor(req.status)}` }}></div>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{req.status}</span>
                      </div>
                     </td>
                     <td style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Clock size={14} /> {new Date(req.submitted_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                      </div>
                     </td>
                   </tr>
                 ))}
               </tbody>
             </table>
             {requests.length === 0 && (
              <div style={{ textAlign: 'center', padding: '8rem 0', color: 'var(--text-muted)' }}>
                <Activity size={64} style={{ marginBottom: '1.5rem', opacity: 0.2 }} />
                <p style={{ fontSize: '1.1rem' }}>No active transmissions found in the network.</p>
              </div>
             )}
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.5rem' }} className="fade-in">
             {patients.map((p) => (
               <div key={p.patient_id} className="card patient-card" style={patientCardStyle}>
                 <div style={patientCardHeaderStyle(p.blood_type)}>
                    <UserCheck size={20} />
                    <span style={{ fontWeight: 800 }}>{p.blood_type}</span>
                 </div>
                 <div style={{ padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>{p.first_name} {p.last_name}</h3>
                    <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginBottom: '1.5rem', fontFamily: 'monospace' }}>ID: {p.patient_id}</p>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                      <div className="stat-pill">
                        <span className="label">Age</span>
                        <div className="val">{p.age}y</div>
                      </div>
                      <div className="stat-pill">
                        <span className="label">Diagnosis</span>
                        <div className="val" title={p.diagnosis}>{p.diagnosis || 'Standard'}</div>
                      </div>
                    </div>
                    
                    <button className="btn-action">
                      View EHR <ChevronRight size={16} />
                    </button>
                 </div>
               </div>
             ))}
             {patients.length === 0 && (
               <div className="glass" style={{ gridColumn: '1/-1', textAlign: 'center', padding: '8rem 0', borderRadius: '2rem', borderStyle: 'dashed' }}>
                 <Users size={64} style={{ marginBottom: '1.5rem', opacity: 0.2 }} />
                 <p style={{ fontSize: '1.1rem', color: 'var(--text-dim)' }}>The registry is currently empty.</p>
               </div>
             )}
          </div>
        )}
      </section>

      {/* MODALS */}
      {(showPatientModal || showRequestModal) && (
        <div className="modal-overlay">
          <div className="card modal-content fade-in" style={{ maxWidth: showPatientModal ? '600px' : '500px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>{showPatientModal ? 'Register New Patient' : 'Emergency Blood Request'}</h2>
              <button onClick={() => { setShowPatientModal(false); setShowRequestModal(false); setErrorMsg(''); }} style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}>
                <Plus style={{ transform: 'rotate(45deg)' }} />
              </button>
            </div>

            {errorMsg && (
              <div className="error-alert">
                <AlertCircle size={20} />
                <div>
                  <div style={{ fontWeight: 700 }}>Operation Failed</div>
                  <div style={{ fontSize: '0.85rem', opacity: 0.9 }}>{errorMsg}</div>
                </div>
              </div>
            )}

            {showPatientModal ? (
              <form onSubmit={handleAddPatient}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  <div className="input-group">
                    <label className="label">First Name</label>
                    <input type="text" className="input" placeholder="e.g. John" onChange={e => setNewPatient({...newPatient, first_name: e.target.value})} required />
                  </div>
                  <div className="input-group">
                    <label className="label">Last Name</label>
                    <input type="text" className="input" placeholder="e.g. Doe" onChange={e => setNewPatient({...newPatient, last_name: e.target.value})} required />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  <div className="input-group">
                    <label className="label">Age</label>
                    <input type="number" className="input" min="0" max="150" value={newPatient.age} onChange={e => setNewPatient({...newPatient, age: parseInt(e.target.value)})} required />
                  </div>
                  <div className="input-group">
                    <label className="label">Blood Group</label>
                    <select className="input" value={newPatient.blood_type} onChange={e => setNewPatient({...newPatient, blood_type: e.target.value})}>
                      {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(t => <option key={t}>{t}</option>)}
                    </select>
                  </div>
                </div>
                <div className="input-group">
                  <label className="label">Admission Diagnosis</label>
                  <textarea className="input" style={{ minHeight: '100px' }} placeholder="Clinical notes..." onChange={e => setNewPatient({...newPatient, diagnosis: e.target.value})} />
                </div>
                <div style={{ marginTop: '2.5rem', display: 'flex', gap: '1rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Confirm Registration</button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleCreateRequest}>
                <div className="input-group">
                  <label className="label">Select Subject</label>
                  <select className="input" onChange={e => setNewRequest({...newRequest, patient: e.target.value})} required>
                    <option value="">Search patient registry...</option>
                    {patients.map(p => (
                      <option key={p.patient_id} value={p.patient_id}>{p.first_name} {p.last_name} ({p.blood_type})</option>
                    ))}
                  </select>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                  <div className="input-group">
                    <label className="label">Requirement</label>
                    <select className="input" value={newRequest.blood_type} onChange={e => setNewRequest({...newRequest, blood_type: e.target.value})}>
                       {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(t => <option key={t}>{t}</option>)}
                    </select>
                  </div>
                  <div className="input-group">
                    <label className="label">Quantity (Units)</label>
                    <input type="number" className="input" min="1" value={newRequest.units_required} onChange={e => setNewRequest({...newRequest, units_required: parseInt(e.target.value)})} required />
                  </div>
                </div>
                <div className="input-group">
                  <label className="label">Urgency Level</label>
                  <select className="input" value={newRequest.priority} onChange={e => setNewRequest({...newRequest, priority: e.target.value})}>
                    <option value="NORMAL">Normal Supply</option>
                    <option value="URGENT">Urgent (24h)</option>
                    <option value="EMERGENCY">CRITICAL EMERGENCY</option>
                  </select>
                </div>
                <div style={{ marginTop: '2.5rem' }}>
                  <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Dispatch Emergency Order</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Styled Components Mock */}
      <style>{`
        .hospital-portal {
          padding: 1rem 0;
        }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          border-radius: 1rem;
          border: none;
          background: none;
          color: var(--text-dim);
          cursor: pointer;
          transition: all 0.3s;
          font-weight: 600;
          position: relative;
        }
        .nav-item:hover {
          background: rgba(255,255,255,0.03);
          color: white;
        }
        .nav-item.active {
          background: var(--primary-glow);
          color: var(--primary);
        }
        .nav-badge {
          margin-left: auto;
          background: var(--primary);
          color: white;
          font-size: 0.7rem;
          padding: 0.2rem 0.5rem;
          border-radius: 100px;
        }
        .blood-chip {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(239, 35, 60, 0.1);
          color: var(--primary);
          padding: 0.4rem 0.8rem;
          border-radius: 0.5rem;
          font-weight: 800;
          font-size: 0.9rem;
        }
        .patient-card {
          padding: 0 !important;
          overflow: hidden;
          transition: transform 0.3s, border-color 0.3s;
        }
        .patient-card:hover {
          transform: translateY(-5px);
          border-color: var(--primary);
        }
        .stat-pill {
          background: var(--bg-surface);
          padding: 0.75rem;
          border-radius: 0.75rem;
          border: 1px solid var(--glass-border);
        }
        .stat-pill .label {
          font-size: 0.65rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: 0.25rem;
        }
        .stat-pill .val {
          font-weight: 700;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .btn-action {
          width: 100%;
          justify-content: center;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background: rgba(255,255,255,0.03);
          border: 1px solid var(--glass-border);
          border-radius: 0.75rem;
          color: white;
          font-weight: 600;
          cursor: pointer;
          transition: 0.2s;
        }
        .btn-action:hover {
          background: var(--primary);
          border-color: var(--primary);
        }
        .modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.8);
          backdrop-filter: blur(12px);
          z-index: 2000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }
        .error-alert {
          display: flex;
          gap: 1rem;
          background: rgba(239, 71, 111, 0.1);
          border: 1px solid rgba(239, 71, 111, 0.2);
          padding: 1rem;
          border-radius: 0.75rem;
          color: #ef476f;
          margin-bottom: 2rem;
        }
      `}</style>
    </div>
  );
};

const navItemStyle = (active) => ({
  // Handled by CSS classes above
});

const patientCardStyle = {
  // Handled by CSS classes above
};

const patientCardHeaderStyle = (type) => ({
  background: 'linear-gradient(135deg, var(--bg-surface) 0%, rgba(239, 35, 60, 0.1) 100%)',
  padding: '1.25rem 1.5rem',
  borderBottom: '1px solid var(--glass-border)',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  color: 'var(--primary)'
});

const getStatusColor = (status) => {
  switch(status) {
    case 'PENDING': return '#ffd166';
    case 'APPROVED': return '#06d6a0';
    case 'FULFILLED': return '#118ab2';
    default: return '#ef476f';
  }
};

export default HospitalDashboard;
