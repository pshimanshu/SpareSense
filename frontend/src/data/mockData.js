export const mockUser = {
  name: "Alex Chen",
  role: "College Student",
  totalSaved: 47.23,
  weekSaved: 12.84
};

export const mockTransactions = [
  { id: 1, merchant: "Starbucks", amount: 4.35, category: "Coffee", date: "2025-01-23", roundUp: 0.65 },
  { id: 2, merchant: "Uber Eats", amount: 18.20, category: "Food Delivery", date: "2025-01-23", roundUp: 0.80 },
  { id: 3, merchant: "Netflix", amount: 15.99, category: "Subscriptions", date: "2025-01-22", roundUp: 0.01 },
  { id: 4, merchant: "Chipotle", amount: 12.47, category: "Food Delivery", date: "2025-01-22", roundUp: 0.53 },
  { id: 5, merchant: "Starbucks", amount: 5.82, category: "Coffee", date: "2025-01-21", roundUp: 0.18 },
  { id: 6, merchant: "Amazon Prime", amount: 14.99, category: "Subscriptions", date: "2025-01-20", roundUp: 0.01 },
  { id: 7, merchant: "DoorDash", amount: 23.15, category: "Food Delivery", date: "2025-01-20", roundUp: 0.85 },
  { id: 8, merchant: "Spotify", amount: 10.99, category: "Subscriptions", date: "2025-01-19", roundUp: 0.01 },
];

export const mockSpendingData = [
  { category: "Food Delivery", amount: 310, color: "#F59E0B" },
  { category: "Coffee", amount: 142, color: "#8B5CF6" },
  { category: "Subscriptions", amount: 89, color: "#EC4899" },
  { category: "Other", amount: 156, color: "#6366F1" }
];

export const mockAIInsights = [
  {
    type: "alert",
    message: "You spent 3x more on food delivery than groceries last month"
  },
  {
    type: "tip",
    message: "Order delivery 1x/week less → Save ~$80/month",
    savings: 80
  },
  {
    type: "tip",
    message: "Brew coffee at home 2 days/week → Save ~$35/month",
    savings: 35
  }
];

export const mockFlashcards = [
  {
    id: 1,
    question: "Which category did you overspend on last month?",
    answer: "Food Delivery ($310) - that's 44% of your discretionary spending!",
    answered: false
  },
  {
    id: 2,
    question: "If you cut coffee spending by 20%, how much would you save per month?",
    answer: "About $28/month or $336/year!",
    answered: false
  },
  {
    id: 3,
    question: "True or False: Subscriptions are your #1 silent expense",
    answer: "False! Food delivery costs you 3.5x more than all subscriptions combined.",
    answered: false
  },
  {
    id: 4,
    question: "How much did micro-roundups save you this week?",
    answer: "$12.84 - completely invisible savings!",
    answered: false
  },
  {
    id: 5,
    question: "What's one habit you can change this week to save money?",
    answer: "Try cooking at home twice instead of ordering delivery. Start small!",
    answered: false
  }
];