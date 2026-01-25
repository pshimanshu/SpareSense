import { useState, useEffect } from 'react';
import { AlertCircle, Lightbulb, TrendingUp, Sparkles } from 'lucide-react';
import { mockAIInsights } from '../data/mockData';
import { apiService } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

export default function AIInsights({ demoMode }) {
  const [insights, setInsights] = useState(mockAIInsights);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiService.getAIInsights(demoMode);
        setInsights(response.data);
      } catch (err) {
        setError('Failed to load AI insights');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [demoMode]);

  const handleGenerateMore = async () => {
    setGenerating(true);
    try {
      const response = await apiService.generateMoreInsights(demoMode, { insights });
      setInsights([...insights, ...response.data]);
    } catch (err) {
      console.error('Failed to generate more insights:', err);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="card"><LoadingSpinner /></div>;
  if (error) return <div className="card"><ErrorMessage message={error} /></div>;

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
      <div className={`rounded-lg p-4 border mb-4 ${getBackgroundClass(insights[0].type)}`}>
        <div className="flex items-start gap-3">
          {getIcon(insights[0].type)}
          <div>
            <p className="text-sm font-medium text-white leading-relaxed">
              {insights[0].message}
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
        
        {insights.slice(1).map((insight, index) => (
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
            ${insights
              .filter(i => i.savings)
              .reduce((sum, i) => sum + i.savings, 0)}
          </span>
        </div>
      </div>

      {/* Action Button */}
      <button 
        onClick={handleGenerateMore}
        disabled={generating}
        className="w-full mt-4 btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {generating ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <Sparkles className="w-4 h-4" />
            Generate More Tips
          </>
        )}
      </button>
    </div>
  );
}