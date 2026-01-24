import { useState } from 'react';
import Header from '../components/Header';
import SpendingChart from '../components/SpendingChart';
import AIInsights from '../components/AIInsights';
import Flashcard from '../components/Flashcard';
import { mockUser } from '../data/mockData';

export default function Dashboard() {
  const [demoMode, setDemoMode] = useState(true);

  return (
    <div className="min-h-screen">
      <Header 
        user={mockUser} 
        demoMode={demoMode}
        onToggleDemo={() => setDemoMode(!demoMode)}
      />
      
      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Spending Chart */}
          <div className="col-span-5">
            <SpendingChart />
          </div>

          {/* AI Insights */}
          <div className="col-span-7">
            <AIInsights />
          </div>

          {/* Flashcard - Now functional! */}
          <div className="col-span-12">
            <Flashcard />
          </div>

          <div className="col-span-12 card">
            <h2 className="text-lg font-semibold mb-4">💸 Microsavings Meter</h2>
            <div className="h-40 flex items-center justify-center text-gray-500">
              Savings meter coming in Batch 5
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}