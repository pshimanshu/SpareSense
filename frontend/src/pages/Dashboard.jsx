import { useState, useEffect } from 'react';
import Header from '../components/Header';
import SpendingChart from '../components/SpendingChart';
import AIInsights from '../components/AIInsights';
import Flashcard from '../components/Flashcard';
import SavingsMeter from '../components/SavingsMeter';
import { mockUser } from '../data/mockData';
import { apiService } from '../services/api';

export default function Dashboard() {
  const [demoMode, setDemoMode] = useState(true);
  const [customerName, setCustomerName] = useState('');
  const [userData, setUserData] = useState(mockUser);
  const [loading, setLoading] = useState(false);

  // Fetch customer data when name changes
  useEffect(() => {
    const fetchCustomerData = async () => {
      if (!demoMode && customerName) {
        setLoading(true);
        try {
          const response = await apiService.getCustomerByName(demoMode, customerName);
          if (response.data && response.data.length > 0) {
            const customer = response.data[0];
            // Calculate total saved from transactions
            const transactions = customer.transactions || [];
            const totalRoundUps = transactions.reduce((sum, tx) => {
              const roundUp = Math.ceil(tx.amount) - tx.amount;
              return sum + roundUp;
            }, 0);
            
            setUserData({
              name: customer.name,
              role: "Customer",
              totalSaved: parseFloat(totalRoundUps.toFixed(2)),
              weekSaved: parseFloat((totalRoundUps * 0.3).toFixed(2))
            });
          }
        } catch (err) {
          console.error('Failed to fetch customer data:', err);
        } finally {
          setLoading(false);
        }
      } else if (demoMode) {
        setUserData(mockUser);
      }
    };

    fetchCustomerData();
  }, [demoMode, customerName]);

  return (
    <div className="min-h-screen">
      <Header 
        user={userData} 
        demoMode={demoMode}
        onToggleDemo={() => setDemoMode(!demoMode)}
        customerName={customerName}
        onCustomerNameChange={setCustomerName}
        loading={loading}
      />
      
      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Spending Chart */}
          <div className="col-span-5">
            <SpendingChart demoMode={demoMode} customerName={customerName} />
          </div>

          {/* AI Insights */}
          <div className="col-span-7">
            <AIInsights demoMode={demoMode} customerName={customerName} />
          </div>

          {/* Flashcard */}
          <div className="col-span-12">
            <Flashcard demoMode={demoMode} />
          </div>

          {/* Microsavings Meter */}
          <div className="col-span-12">
            <SavingsMeter demoMode={demoMode} customerName={customerName} />
          </div>
        </div>
      </main>
    </div>
  );
}