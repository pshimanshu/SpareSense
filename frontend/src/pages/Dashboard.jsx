import { useState } from 'react';
import Header from '../components/Header';
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
          {/* Placeholder sections - we'll build these in next batches */}
          <div className="col-span-5 card">
            <h2 className="text-lg font-semibold mb-4">📊 Spending Breakdown</h2>
            <div className="h-64 flex items-center justify-center text-gray-500">
              Chart coming in Batch 2
            </div>
          </div>

          <div className="col-span-7 card">
            <h2 className="text-lg font-semibold mb-4">🧠 AI Insights</h2>
            <div className="h-64 flex items-center justify-center text-gray-500">
              AI insights coming in Batch 3
            </div>
          </div>

          <div className="col-span-12 card">
            <h2 className="text-lg font-semibold mb-4">🎴 Financial Literacy Flashcard</h2>
            <div className="h-48 flex items-center justify-center text-gray-500">
              Flashcard coming in Batch 4
            </div>
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