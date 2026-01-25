import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { mockSpendingData } from '../data/mockData';
import { apiService } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

export default function SpendingChart({ demoMode, customerName }) {
  const [spendingData, setSpendingData] = useState(mockSpendingData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSpendingData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiService.getSpendingBreakdown(demoMode, customerName);
        setSpendingData(response.data);
      } catch (err) {
        setError('Failed to load spending data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSpendingData();
  }, [demoMode, customerName]);

  if (loading) return <div className="card"><LoadingSpinner /></div>;
  if (error) return <div className="card"><ErrorMessage message={error} /></div>;

  const totalSpending = spendingData.reduce((sum, item) => sum + item.amount, 0);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = ((data.value / totalSpending) * 100).toFixed(1);
      return (
        <div className="bg-dark-card border border-dark-border rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-white">{data.name}</p>
          <p className="text-success font-bold">${data.value}</p>
          <p className="text-gray-400 text-sm">{percentage}% of spending</p>
        </div>
      );
    }
    return null;
  };

  // Custom label to show percentage on chart
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * (Math.PI / 180));
    const y = cy + radius * Math.sin(-midAngle * (Math.PI / 180));

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        className="text-sm font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">📊 Spending Breakdown</h2>
      
      {/* Total Spending */}
      <div className="text-center mb-6">
        <p className="text-gray-400 text-sm">Last 30 Days</p>
        <p className="text-3xl font-bold text-white">${totalSpending}</p>
      </div>

      {/* Pie Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={spendingData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={90}
            innerRadius={50}
            fill="#8884d8"
            dataKey="amount"
            nameKey="category"
          >
            {spendingData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend with amounts */}
      <div className="mt-6 space-y-2">
        {spendingData.map((item) => (
          <div key={item.category} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-gray-300">{item.category}</span>
            </div>
            <span className="font-semibold text-white">${item.amount}</span>
          </div>
        ))}
      </div>
    </div>
  );
}