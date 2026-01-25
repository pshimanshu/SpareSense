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
        // In demo mode, pass empty string to use mock data
        // In live mode, pass customerName
        const nameParam = demoMode ? '' : customerName;
        const response = await apiService.getSpendingBreakdown(demoMode, nameParam);
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

  // Color palette for categories
  const categoryColors = [
    '#F59E0B', // Amber
    '#EC4899', // Pink
    '#8B5CF6', // Purple
    '#10B981', // Emerald
    '#3B82F6', // Blue
    '#EF4444', // Red
    '#14B8A6', // Teal
  ];

  // Keep max 7 categories, combine smallest ones if more than 7
  const processedData = (() => {
    if (spendingData.length <= 7) {
      // If 7 or fewer categories, keep all and assign colors
      return spendingData.map((item, index) => ({
        ...item,
        amount: parseFloat(item.amount.toFixed(2)),
        color: categoryColors[index % categoryColors.length]
      }));
    }

    // Sort by amount descending
    const sorted = [...spendingData].sort((a, b) => b.amount - a.amount);
    
    // Keep top 6 categories
    const topCategories = sorted.slice(0, 6).map((item, index) => ({
      ...item,
      amount: parseFloat(item.amount.toFixed(2)),
      color: categoryColors[index]
    }));
    
    // Combine remaining into Misc
    const remaining = sorted.slice(6);
    const miscAmount = remaining.reduce((sum, item) => sum + item.amount, 0);
    
    topCategories.push({
      category: 'Misc',
      amount: parseFloat(miscAmount.toFixed(2)),
      color: categoryColors[6]
    });

    return topCategories;
  })();

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = ((data.value / totalSpending) * 100).toFixed(1);
      return (
        <div className="bg-dark-card border border-dark-border rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-white">{data.name}</p>
          <p className="text-success font-bold">${data.value.toFixed(2)}</p>
          <p className="text-gray-400 text-sm">{percentage}% of spending</p>
        </div>
      );
    }
    return null;
  };

  // Custom label to show percentage on chart
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    // Position label in the middle of the slice
    const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
    const x = cx + radius * Math.cos(-midAngle * (Math.PI / 180));
    const y = cy + radius * Math.sin(-midAngle * (Math.PI / 180));

    // Only show label if percentage is above 5% to avoid clutter
    if (percent < 0.05) return null;

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor="middle" 
        dominantBaseline="central"
        className="text-sm font-bold"
        style={{ pointerEvents: 'none' }}
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
        <p className="text-3xl font-bold text-white">${totalSpending.toFixed(2)}</p>
      </div>

      {/* Pie Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={processedData}
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
            {processedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend with amounts */}
      <div className="mt-6 space-y-2">
        {processedData.map((item) => (
          <div key={item.category} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-gray-300">{item.category}</span>
            </div>
            <span className="font-semibold text-white">${item.amount.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}