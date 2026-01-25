import { DollarSign, TrendingUp } from 'lucide-react';

export default function Header({ user, demoMode, onToggleDemo }) {
  return (
    <header className="bg-dark-card border-b border-dark-border px-8 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left: Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="bg-primary/20 p-2 rounded-lg">
            <DollarSign className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">FinWise</h1>
            <p className="text-xs text-gray-400">AI Financial Coach</p>
          </div>
        </div>

        {/* Center: User Info */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="font-semibold">{user.name}</p>
            <p className="text-sm text-gray-400">{user.role}</p>
          </div>
        </div>

        {/* Right: Savings Summary */}
        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-sm text-gray-400">Total Saved</p>
            <p className="text-2xl font-bold text-success">
              ${user.totalSaved.toFixed(2)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400 flex items-center gap-1">
              This Week <TrendingUp className="w-3 h-3" />
            </p>
            <p className="text-xl font-semibold text-primary">
              +${user.weekSaved.toFixed(2)}
            </p>
          </div>
          
          {/* Demo Mode Toggle */}
          <button
            onClick={onToggleDemo}
            className={`px-3 py-1 rounded-full text-xs font-medium border ${
              demoMode
                ? 'bg-warning/20 border-warning text-warning'
                : 'bg-dark-border border-dark-border text-gray-400'
            }`}
          >
            {demoMode ? '🎬 Demo Mode' : 'Live Mode'}
          </button>
        </div>
      </div>
    </header>
  );
}