import axios from 'axios';
import { 
  mockUser, 
  mockTransactions, 
  mockSpendingData, 
  mockAIInsights, 
  mockFlashcards 
} from '../data/mockData';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
  async getAIInsights(useMockData = false, spendingData) {
    if (useMockData) {
      await mockDelay(1000); // Longer delay for AI simulation
      return { data: mockAIInsights };
    }
    // Send spending data to backend, which calls Gemini API
    const response = await apiClient.post('/ai/insights', { spendingData });
    return response;
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
    const response = await apiClient.post('/ai/insights/generate', { context });
    return response;
  },

  // Flashcards
  async getFlashcards(useMockData = false, userId) {
    if (useMockData) {
      await mockDelay();
      return { data: mockFlashcards };
    }
    const response = await apiClient.get(`/flashcards/${userId}`);
    return response;
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