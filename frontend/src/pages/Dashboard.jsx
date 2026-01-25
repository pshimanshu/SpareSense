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
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Calculate savings from transactions
  const calculateSavings = (txs) => {
    const totalRoundUps = txs.reduce((sum, tx) => {
      const roundUp = tx.roundUp || (Math.ceil(tx.amount) - tx.amount);
      return sum + roundUp;
    }, 0);

    // Calculate this week's savings (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const weekTransactions = txs.filter(tx => {
      const txDate = new Date(tx.date);
      return txDate >= sevenDaysAgo;
    });
    const weekRoundUps = weekTransactions.reduce((sum, tx) => {
      const roundUp = tx.roundUp || (Math.ceil(tx.amount) - tx.amount);
      return sum + roundUp;
    }, 0);

    return {
      totalSaved: parseFloat(totalRoundUps.toFixed(2)),
      weekSaved: parseFloat(weekRoundUps.toFixed(2))
    };
  };

  // Fetch customer data when name changes
  useEffect(() => {
    const fetchCustomerData = async () => {
      if (demoMode) {
        // In demo mode, always use mock data
        const response = await apiService.getTransactions(true, '');
        setTransactions(response.data);
        const savings = calculateSavings(response.data);
        setUserData({
          ...mockUser,
          ...savings
        });
        return;
      }

      if (!customerName) {
        // In live mode without a name, show default
        setTransactions([]);
        setUserData({
          name: "Enter customer name",
          role: "Guest",
          totalSaved: 0,
          weekSaved: 0
        });
        return;
      }

      // Fetch real customer data
      setLoading(true);
      try {
        const response = await apiService.getCustomerByName(false, customerName);
        if (response.data && response.data.length > 0) {
          const customer = response.data[0];
          // Get transactions with round-ups
          const txResponse = await apiService.getTransactions(false, customerName);
          setTransactions(txResponse.data);
          const savings = calculateSavings(txResponse.data);
          
          setUserData({
            name: customer.name || customerName,
            role: customer.transaction_count > 0 ? "Premium Member" : "Member",
            ...savings
          });
        } else {
          // No customer found
          setTransactions([]);
          setUserData({
            name: "Customer not found",
            role: "Guest",
            totalSaved: 0,
            weekSaved: 0
          });
        }
      } catch (err) {
        console.error('Failed to fetch customer data:', err);
        setTransactions([]);
        setUserData({
          name: "Error loading data",
          role: "Guest",
          totalSaved: 0,
          weekSaved: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCustomerData();
  }, [demoMode, customerName]);

  // Update savings whenever transactions change
  useEffect(() => {
    if (transactions.length > 0) {
      const savings = calculateSavings(transactions);
      setUserData(prev => ({
        ...prev,
        ...savings
      }));
    }
  }, [transactions]);

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
            <SavingsMeter 
              demoMode={demoMode} 
              customerName={customerName}
              transactions={transactions}
              onTransactionsUpdate={setTransactions}
            />
          </div>
        </div>
      </main>
    </div>
  );
}