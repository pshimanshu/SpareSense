import { AlertCircle, Lightbulb, TrendingUp, Sparkles } from 'lucide-react';
import { mockAIInsights } from '../data/mockData';

export default function AIInsights() {
  const getIcon = (type) => {
    switch (type) {
      case 'alert':
        return <AlertCircle className="w-5 h-5 text-warning" />;
      case 'tip':
        return <Lightbulb className="w-5 h-5 text-primary" />;
      default:
        return <Sparkles className="w-5 h-5 text-success" />;
    }
  };

  const getBackgroundClass = (type) => {
    switch (type) {
      case 'alert':
        return 'bg-warning/10 border-warning/30';
      case 'tip':
        return 'bg-primary/10 border-primary/30';
      default:
        return 'bg-success/10 border-success/30';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">🧠 AI Insights</h2>
        <div className="flex items-center gap-1 text-xs text-gray-400">
          <Sparkles className="w-3 h-3" />
          <span>Powered by Gemini</span>
        </div>
      </div>

      {/* Main Alert */}
      <div className={`rounded-lg p-4 border mb-4 ${getBackgroundClass(mockAIInsights[0].type)}`}>
        <div className="flex items-start gap-3">
          {getIcon(mockAIInsights[0].type)}
          <div>
            <p className="text-sm font-medium text-white leading-relaxed">
              {mockAIInsights[0].message}
            </p>
          </div>
        </div>
      </div>

      {/* Savings Tips */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-success" />
          Personalized Savings Opportunities
        </h3>
        
        {mockAIInsights.slice(1).map((insight, index) => (
          <div 
            key={index}
            className={`rounded-lg p-4 border ${getBackgroundClass(insight.type)} hover:border-primary/50 transition-colors cursor-pointer`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 flex-1">
                {getIcon(insight.type)}
                <p className="text-sm text-gray-200 leading-relaxed">
                  {insight.message}
                </p>
              </div>
              {insight.savings && (
                <div className="text-right shrink-0">
                  <p className="text-lg font-bold text-success">
                    ${insight.savings}
                  </p>
                  <p className="text-xs text-gray-400">per month</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Total Potential Savings */}
      <div className="mt-4 pt-4 border-t border-dark-border">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Potential Monthly Savings</span>
          <span className="text-xl font-bold text-success">
            ${mockAIInsights
              .filter(i => i.savings)
              .reduce((sum, i) => sum + i.savings, 0)}
          </span>
        </div>
      </div>

      {/* Action Button */}
      <button className="w-full mt-4 btn-primary flex items-center justify-center gap-2">
        <Sparkles className="w-4 h-4" />
        Generate More Tips
      </button>
    </div>
  );
}