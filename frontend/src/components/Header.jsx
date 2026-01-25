import { DollarSign, TrendingUp, Search } from 'lucide-react';
import { useState } from 'react';

export default function Header({ user, demoMode, onToggleDemo, customerName, onCustomerNameChange, loading }) {
  const [searchInput, setSearchInput] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onCustomerNameChange(searchInput.trim());
    }
  };

  return (
    <header className="bg-dark-card border-b border-dark-border px-8 py-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
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
            <div className="text-center">
              <p className="font-semibold text-lg">{user.name}</p>
              <p className="text-sm text-gray-400">{user.role}</p>
            </div>
          </div>

          {/* Right: Search, Savings Summary & Toggle */}
          <div className="flex items-center gap-4">
            {/* Customer Search */}
            {!demoMode && (
              <form onSubmit={handleSearch} className="flex items-center gap-2">
                <div className="relative">
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Search customer..."
                    className="bg-dark-border text-white px-4 py-2 pr-10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary w-48"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </form>
            )}

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
      </div>
    </header>
  );
}