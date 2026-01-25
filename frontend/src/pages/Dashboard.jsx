import { useState } from 'react';
import Header from '../components/Header';
import SpendingChart from '../components/SpendingChart';
import AIInsights from '../components/AIInsights';
import Flashcard from '../components/Flashcard';
import { mockFlashcards } from '../data/mockData';
import SavingsMeter from '../components/SavingsMeter';
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

          {/* Flashcard */}
          <div className="col-span-12">
            <Flashcard flashcardsData={mockFlashcards} />
          </div>

          {/* Microsavings Meter - Now functional! */}
          <div className="col-span-12">
            <SavingsMeter />
          </div>
        </div>
      </main>
    </div>
  );
}