import { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, Zap, Plus } from 'lucide-react';
import { mockTransactions } from '../data/mockData';
import { apiService } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

export default function SavingsMeter({ demoMode, customerName }) {
  const [transactions, setTransactions] = useState(mockTransactions);
  const [isSimulating, setIsSimulating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiService.getTransactions(demoMode, customerName);
        setTransactions(response.data);
      } catch (err) {
        setError('Failed to load transactions');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [demoMode, customerName]);

  // Calculate totals
  const totalRoundUps = transactions.reduce((sum, tx) => sum + tx.roundUp, 0);
  const todayTransactions = transactions.filter(tx => tx.date === "2025-01-23");
  const todayRoundUps = todayTransactions.reduce((sum, tx) => sum + tx.roundUp, 0);

  // Progress to next $5 milestone
  const nextMilestone = Math.max(5, Math.ceil(totalRoundUps / 5) * 5);
  const progressPercent = (totalRoundUps / nextMilestone) * 100;

  // Simulate a new transaction
  const simulateTransaction = async () => {
    setIsSimulating(true);
    
    const merchants = ['Starbucks', 'Chipotle', 'Target', 'Gas Station', 'Grocery Store'];
    const categories = ['Coffee', 'Food', 'Shopping', 'Gas', 'Groceries'];
    const randomAmount = (Math.random() * 30 + 5).toFixed(2);
    const amount = parseFloat(randomAmount);
    const roundUp = parseFloat((Math.ceil(amount) - amount).toFixed(2));

    const newTransactionData = {
      merchant: merchants[Math.floor(Math.random() * merchants.length)],
      amount: amount,
      category: categories[Math.floor(Math.random() * categories.length)],
    };

    try {
      const response = await apiService.createTransaction(demoMode, newTransactionData);
      // Add to top of list
      setTransactions([response.data, ...transactions]);
    } catch (err) {
      console.error('Failed to create transaction:', err);
    } finally {
      setTimeout(() => setIsSimulating(false), 1000);
    }
  };

  if (loading) return <div className="card"><LoadingSpinner /></div>;
  if (error) return <div className="card"><ErrorMessage message={error} /></div>;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">💸 Microsavings Meter</h2>
        <button
          onClick={simulateTransaction}
          disabled={isSimulating}
          className="btn-primary flex items-center gap-2 disabled:opacity-50"
        >
          {isSimulating ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" />
              Simulate Transaction
            </>
          )}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {/* Total Saved */}
        <div className="bg-gradient-to-br from-success/20 to-emerald-600/20 border border-success/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-success" />
            <span className="text-xs text-gray-400">Total Saved</span>
          </div>
          <p className="text-2xl font-bold text-success">
            ${totalRoundUps.toFixed(2)}
          </p>
        </div>

        {/* Today's Savings */}
        <div className="bg-gradient-to-br from-primary/20 to-purple-600/20 border border-primary/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-primary" />
            <span className="text-xs text-gray-400">Saved Today</span>
          </div>
          <p className="text-2xl font-bold text-primary">
            ${todayRoundUps.toFixed(2)}
          </p>
        </div>

        {/* Transactions */}
        <div className="bg-gradient-to-br from-warning/20 to-orange-600/20 border border-warning/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-warning" />
            <span className="text-xs text-gray-400">Round-Ups</span>
          </div>
          <p className="text-2xl font-bold text-warning">
            {transactions.length}
          </p>
        </div>
      </div>

      {/* Progress to Next Milestone */}
      <div className="mb-6 p-4 bg-dark-border/30 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-300">Progress to ${nextMilestone}</span>
          <span className="text-sm font-semibold text-success">
            ${(nextMilestone - totalRoundUps).toFixed(2)} to go
          </span>
        </div>
        <div className="w-full bg-dark-border rounded-full h-3 overflow-hidden">
          <div 
            className="bg-gradient-to-r from-success to-emerald-400 h-3 rounded-full transition-all duration-500 relative"
            style={{ width: `${progressPercent}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          {progressPercent >= 100 ? '🎉 Milestone reached! Ready to invest in Solana' : 'Keep going! Every purchase counts'}
        </p>
      </div>

      {/* Recent Round-Ups */}
      <div>
        <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
          📅 Recent Round-Ups
        </h3>
        <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
          {transactions.slice(0, 8).map((tx, index) => (
            <div 
              key={tx.id}
              className={`flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-primary/30 transition-all ${
                index === 0 && isSimulating ? 'animate-slideIn bg-primary/10' : 'bg-dark-card'
              }`}
            >
              <div className="flex items-center gap-3 flex-1">
                <div className="w-10 h-10 rounded-full bg-dark-border flex items-center justify-center">
                  <span className="text-lg">
                    {tx.category === 'Coffee' ? '☕' : 
                     tx.category === 'Food Delivery' ? '🍔' :
                     tx.category === 'Subscriptions' ? '🎮' :
                     tx.category === 'Food' ? '🍕' :
                     tx.category === 'Shopping' ? '🛍️' :
                     tx.category === 'Gas' ? '⛽' :
                     '🛒'}
                  </span>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-white text-sm">{tx.merchant}</p>
                  <p className="text-xs text-gray-400">{tx.category} • {tx.date}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">${tx.amount.toFixed(2)}</p>
                <p className="text-xs font-semibold text-success">
                  +${tx.roundUp.toFixed(2)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Solana Investment Info */}
      <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="text-2xl">🌐</div>
          <div>
            <h4 className="font-semibold text-white mb-1">Auto-Invest on Solana</h4>
            <p className="text-sm text-gray-300 leading-relaxed">
              When you reach $5 in round-ups, we automatically invest it into a diversified Solana portfolio. 
              Your spare change, growing on the blockchain.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}