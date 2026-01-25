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

export const mockFlashcards = {
  flashcards: [
    {
      id: "card_1",
      type: "multiple_choice",
      skill: "awareness",
      question: "Which category did you overspend on last month?",
      options: [
        "Coffee",
        "Food Delivery",
        "Subscriptions",
        "Groceries"
      ],
      answer: "Food Delivery",
      explanation: "Food Delivery ($310) - that's 44% of your discretionary spending!",
      difficulty: "easy",
      confidence_score: 0.92,
      data: { 
        category: "Food Delivery", 
        amount: 310,
        percentage: 44
      }
    },
    {
      id: "card_2",
      type: "guess_the_number",
      skill: "prediction",
      question: "If you cut coffee spending by 20%, how much would you save per month?",
      options: [
        "$15",
        "$28",
        "$35",
        "$42"
      ],
      answer: "$28",
      explanation: "About $28/month or $336/year! Your current coffee spending is $142/month.",
      difficulty: "medium",
      confidence_score: 0.88,
      data: { 
        category: "Coffee", 
        current_amount: 142,
        savings_monthly: 28,
        savings_yearly: 336
      }
    },
    {
      id: "card_3",
      type: "true_false",
      skill: "habit_reinforcement",
      question: "True or False: Subscriptions are your #1 silent expense",
      options: [
        "True",
        "False"
      ],
      answer: "False",
      explanation: "False! Food delivery costs you 3.5x more than all subscriptions combined.",
      difficulty: "easy",
      confidence_score: 0.95,
      data: { 
        category: "Subscriptions", 
        amount: 89,
        comparison: "Food delivery is 3.5x more"
      }
    },
    {
      id: "card_4",
      type: "multiple_choice",
      skill: "awareness",
      question: "How much did micro-roundups save you this week?",
      options: [
        "$5.50",
        "$8.75",
        "$12.84",
        "$15.20"
      ],
      answer: "$12.84",
      explanation: "$12.84 - completely invisible savings without you even noticing!",
      difficulty: "medium",
      confidence_score: 0.85,
      data: { 
        feature: "micro-roundups",
        amount: 12.84,
        period: "week"
      }
    },
    {
      id: "card_5",
      type: "reflection",
      skill: "commitment",
      question: "What's the best first step to save money this week?",
      options: [
        "Cancel all subscriptions",
        "Cook at home twice instead of ordering",
        "Stop buying coffee completely",
        "Switch banks"
      ],
      answer: "Cook at home twice instead of ordering",
      explanation: "Try cooking at home twice instead of ordering delivery. Start small and build sustainable habits!",
      difficulty: "easy",
      confidence_score: 0.90,
      data: { 
        recommendation: "Cook at home",
        impact: "Start small, build habits",
        potential_savings: 40
      }
    }
  ],
  meta: {
    generated_by: "mock_data",
    fallback_used: false,
    total_cards: 5,
    user_spending_period: "last_month"
  }
};

// For backwards compatibility, export just the flashcards array if needed
export const mockFlashcardsArray = mockFlashcards.flashcards;