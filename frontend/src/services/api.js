import axios from 'axios';
import { 
  mockUser, 
  mockTransactions, 
  mockSpendingData, 
  mockAIInsights, 
  mockFlashcards 
} from '../data/mockData';

// Backend default port per README (can be overridden via VITE_API_BASE_URL).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5050';

// API Client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth tokens (when needed)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Simulate network delay for realistic mock behavior
const mockDelay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

// Build the DEV-2 AI contract request body expected by:
// - POST /ai/savings-tips
// - POST /ai/flashcards
const buildAiSpendingSummaryRequest = ({
  userId = 'alex_demo',
  currency = 'USD',
  tipCount = 3,
  flashcardCount = 5,
} = {}) => {
  // Use the existing mock data to keep the demo deterministic and easy to wire.
  const category_totals = (mockSpendingData || []).map((c) => ({
    category: c.category,
    amount: Number(c.amount) || 0,
    transaction_count: (mockTransactions || []).filter((t) => t.category === c.category).length,
  }));

  const top_merchants_map = new Map();
  (mockTransactions || []).forEach((t) => {
    const k = t.merchant || 'Unknown';
    const prev = top_merchants_map.get(k) || { merchant: k, amount: 0, transaction_count: 0, category_hint: t.category || null };
    prev.amount += Number(t.amount) || 0;
    prev.transaction_count += 1;
    if (!prev.category_hint && t.category) prev.category_hint = t.category;
    top_merchants_map.set(k, prev);
  });

  const top_merchants = Array.from(top_merchants_map.values())
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5);

  const total_spend = category_totals.reduce((sum, c) => sum + c.amount, 0);
  const transaction_count = (mockTransactions || []).length;

  // Period: use a stable range so precomputed demo outputs are consistent.
  // (Backend AI contract only requires ISO dates; it doesn't require "today".)
  const period = { start_date: '2025-01-01', end_date: '2025-01-31' };

  return {
    schema_version: '1.0',
    user_context: { user_id: userId, currency },
    period,
    income: { monthly_income: null, confidence: 0.5 },
    spending_summary: {
      total_spend,
      transaction_count,
      category_totals,
      top_merchants,
      silent_spenders: [],
      recurring_merchants: [],
    },
    constraints: { tip_count: tipCount, flashcard_count: flashcardCount },
  };
};

// API Service Functions
export const apiService = {
  // User Data
  async getUserData(useMockData = false) {
    if (useMockData) {
      await mockDelay();
      return { data: mockUser };
    }
    const response = await apiClient.get('/user');
    return response;
  },

  // Transactions
  async getTransactions(useMockData = false, params = {}) {
    if (useMockData) {
      await mockDelay();
      return { data: mockTransactions };
    }
    // params can include: { startDate, endDate, category, limit }
    const response = await apiClient.get('/transactions', { params });
    return response;
  },

  async createTransaction(useMockData = false, transactionData) {
    if (useMockData) {
      await mockDelay();
      const newTransaction = {
        id: Date.now(),
        ...transactionData,
        date: new Date().toISOString().split('T')[0],
        roundUp: parseFloat((Math.ceil(transactionData.amount) - transactionData.amount).toFixed(2))
      };
      return { data: newTransaction };
    }
    const response = await apiClient.post('/transactions', transactionData);
    return response;
  },

  // Spending Analysis
  async getSpendingBreakdown(useMockData = false, period = '30days') {
    if (useMockData) {
      await mockDelay();
      return { data: mockSpendingData };
    }
    // period can be: 'week', 'month', '30days', '90days', 'year'
    const response = await apiClient.get('/spending/breakdown', { params: { period } });
    return response;
  },

  // AI Insights
  async getAIInsights(useMockData = false) {
    if (useMockData) {
      await mockDelay(1000); // Longer delay for AI simulation
      return { data: mockAIInsights };
    }
    // Backend DEV-2 endpoint: POST /ai/savings-tips
    const payload = buildAiSpendingSummaryRequest({ userId: 'alex_demo', tipCount: 3 });
    const resp = await apiClient.post('/ai/savings-tips', payload);

    const tipsResp = resp.data;
    const currency = tipsResp?.currency || 'USD';
    const total = tipsResp?.totals?.estimated_monthly_savings_total ?? 0;

    const insights = [
      {
        type: 'alert',
        message: `Estimated monthly savings potential: ${currency} ${Number(total).toFixed(2)}`,
      },
      ...(tipsResp?.tips || []).map((t) => ({
        type: 'tip',
        message: `${t.title} — ${t.recommendation}`,
        savings: t.estimated_monthly_savings,
      })),
    ];

    return { data: insights };
  },

  async generateMoreInsights(useMockData = false, context) {
    if (useMockData) {
      await mockDelay(1500);
      return { 
        data: [
          {
            type: "tip",
            message: "Switch to a cashback credit card for grocery shopping → Save ~$25/month",
            savings: 25
          },
          {
            type: "tip",
            message: "Cancel unused gym membership → Save $50/month",
            savings: 50
          }
        ]
      };
    }
    // Simple approach: request a few more tips and return them in the same UI shape.
    // We keep user_id as alex_demo so precomputed mode works by default.
    const payload = buildAiSpendingSummaryRequest({ userId: 'alex_demo', tipCount: 2 });
    const resp = await apiClient.post('/ai/savings-tips', payload);

    const tips = (resp.data?.tips || []).map((t) => ({
      type: 'tip',
      message: `${t.title} — ${t.recommendation}`,
      savings: t.estimated_monthly_savings,
    }));

    return { data: tips };
  },

  // Flashcards
  async getFlashcards(useMockData = false, userId) {
    if (useMockData) {
      await mockDelay();
      return { data: mockFlashcards };
    }
    // Backend DEV-2 endpoint: POST /ai/flashcards
    const payload = buildAiSpendingSummaryRequest({ userId: userId || 'alex_demo', flashcardCount: 5 });
    const resp = await apiClient.post('/ai/flashcards', payload);

    // Add a confidence_score field so the UI's "sort by confidence" logic keeps working.
    const data = resp.data || {};
    const flashcards = (data.flashcards || []).map((c) => ({ ...c, confidence_score: 0.5 }));
    return { data: { ...data, flashcards } };
  },

  async submitFlashcardAnswer(useMockData = false, cardId, answer, isCorrect) {
    if (useMockData) {
      await mockDelay(300);
      return { data: { success: true } };
    }
    const response = await apiClient.post('/flashcards/submit', {
      cardId,
      answer,
      isCorrect
    });
    return response;
  },

  // Savings/Round-ups
  async getSavingsSummary(useMockData = false) {
    if (useMockData) {
      await mockDelay();
      const totalRoundUps = mockTransactions.reduce((sum, tx) => sum + tx.roundUp, 0);
      const todayTransactions = mockTransactions.filter(tx => tx.date === "2025-01-23");
      const todayRoundUps = todayTransactions.reduce((sum, tx) => sum + tx.roundUp, 0);
      return {
        data: {
          totalSaved: totalRoundUps,
          weekSaved: 12.84,
          todaySaved: todayRoundUps,
          transactionCount: mockTransactions.length
        }
      };
    }
    const response = await apiClient.get('/savings/summary');
    return response;
  },

  // Solana Integration (future)
  async investRoundups(useMockData = false, amount) {
    if (useMockData) {
      await mockDelay(2000);
      return {
        data: {
          success: true,
          transactionHash: '0x' + Math.random().toString(36).substring(2),
          amount: amount
        }
      };
    }
    const response = await apiClient.post('/solana/invest', { amount });
    return response;
  }
};

// Error Handler Utility
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    return {
      message: error.response.data.message || 'Server error occurred',
      status: error.response.status
    };
  } else if (error.request) {
    // Request made but no response
    return {
      message: 'Network error. Please check your connection.',
      status: 0
    };
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      status: -1
    };
  }
};
