import React from 'react';
import { useAuth } from '../context/AuthContext';
import BloodBankDashboard from './BloodBankDashboard';
import HospitalDashboard from './HospitalDashboard';

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="dashboard-container">
      {user.role === 'blood_bank' ? (
        <BloodBankDashboard />
      ) : (
        <HospitalDashboard />
      )}
    </div>
  );
};

export default Dashboard;
