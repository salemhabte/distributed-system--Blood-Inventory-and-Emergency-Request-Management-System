import React, { useState, useEffect } from 'react';
import { bloodBankService } from '../services/api';
import { Database, Plus, Package, Clock, ShieldCheck, MapPin, Droplet } from 'lucide-react';

const BloodBankDashboard = () => {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newBatch, setNewBatch] = useState({
    blood_type: 'A+',
    quantity: 10,
    donation_date: new Date().toISOString().split('T')[0],
    expiry_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    batch_number: `BB${Date.now()}`,
    storage_location: 'Central Cold Storage'
  });

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const response = await bloodBankService.getInventory();
      setInventory(response.data);
    } catch (err) {
      console.error('Failed to fetch inventory', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddBatch = async (e) => {
    e.preventDefault();
    try {
      await bloodBankService.addBatch(newBatch);
      setShowAddModal(false);
      fetchInventory();
    } catch (err) {
      alert('Failed to add blood batch');
    }
  };

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '3rem' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Global Inventory</h1>
          <p style={{ color: 'var(--text-dim)' }}>Monitor and manage blood supply across the network</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          <Plus size={20} /> Add New Batch
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <div className="card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'var(--primary-glow)', padding: '1rem', borderRadius: '1rem', color: 'var(--primary)' }}>
            <Droplet size={32} />
          </div>
          <div>
            <span className="label" style={{ marginBottom: 0 }}>Total Available</span>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{inventory.reduce((acc, curr) => acc + curr.quantity, 0)} <span style={{ fontSize: '1rem', color: 'var(--text-dim)', fontWeight: 400 }}>Units</span></div>
          </div>
        </div>
        <div className="card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ background: 'rgba(6, 214, 160, 0.1)', padding: '1rem', borderRadius: '1rem', color: 'var(--success)' }}>
            <ShieldCheck size={32} />
          </div>
          <div>
            <span className="label" style={{ marginBottom: 0 }}>Active Groups</span>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{inventory.length}</div>
          </div>
        </div>
      </div>

      <section>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <Database size={24} color="var(--primary)" />
          <h2 style={{ fontSize: '1.5rem' }}>Stock Status</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1.5rem' }}>
          {inventory.map((item, idx) => (
            <div key={idx} className="card" style={{ padding: '1.5rem', textAlign: 'center', transition: 'transform 0.2s' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '0.5rem' }}>{item.blood_type}</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>{item.quantity} <span style={{ color: 'var(--text-dim)', fontSize: '0.9rem', fontWeight: 400 }}>Units</span></div>
              <div className={`badge ${item.quantity > 20 ? 'badge-success' : 'badge-danger'}`}>
                {item.quantity > 20 ? 'Optimal' : 'Low Stock'}
              </div>
            </div>
          ))}
          {inventory.length === 0 && !loading && (
            <div className="card" style={{ gridColumn: '1/-1', textAlign: 'center', padding: '4rem', borderStyle: 'dashed' }}>
              <Package size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-dim)' }}>Inventory is currently empty.</p>
            </div>
          )}
        </div>
      </section>

      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)', zIndex: 2000, display: 'flex', alignItems: 'center', justifyCenter: 'center', padding: '2rem' }}>
          <div className="card fade-in" style={{ maxWidth: '500px', width: '100%', margin: 'auto' }}>
            <h2 style={{ marginBottom: '2rem' }}>Register Blood Batch</h2>
            <form onSubmit={handleAddBatch}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div className="input-group">
                  <label className="label">Blood Type</label>
                  <select 
                    className="input"
                    value={newBatch.blood_type} 
                    onChange={e => setNewBatch({...newBatch, blood_type: e.target.value})}
                  >
                    {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div className="input-group">
                  <label className="label">Quantity (Units)</label>
                  <input 
                    type="number" 
                    className="input"
                    value={newBatch.quantity} 
                    onChange={e => setNewBatch({...newBatch, quantity: parseInt(e.target.value)})}
                  />
                </div>
              </div>
              <div className="input-group">
                <label className="label">Storage Location</label>
                <div style={{ position: 'relative' }}>
                  <MapPin size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input 
                    type="text" 
                    className="input"
                    style={{ paddingLeft: '2.5rem' }}
                    value={newBatch.storage_location} 
                    onChange={e => setNewBatch({...newBatch, storage_location: e.target.value})}
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2.5rem' }}>
                <button type="button" className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setShowAddModal(false)}>Discard</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 2 }}>Confirm Deposit</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BloodBankDashboard;
