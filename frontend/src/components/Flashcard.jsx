import { useState } from 'react';
import { RotateCw, Star, ChevronLeft, ChevronRight, CheckCircle, XCircle } from 'lucide-react';
import { mockFlashcards } from '../data/mockData';

export default function Flashcard() {
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [cards, setCards] = useState(mockFlashcards);
  const [rating, setRating] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);

  const currentCard = cards[currentCardIndex];
  const progress = ((currentCardIndex + 1) / cards.length) * 100;

  const handleAnswerSelect = (optionIndex) => {
    setSelectedAnswer(optionIndex);
    // Mark card as answered
    const updatedCards = [...cards];
    updatedCards[currentCardIndex].answered = true;
    updatedCards[currentCardIndex].userAnswer = optionIndex;
    setCards(updatedCards);
  };

  const handleRevealAnswer = () => {
    if (selectedAnswer !== null) {
      setIsFlipped(true);
    }
  };

  const handleNext = () => {
    if (currentCardIndex < cards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
      setIsFlipped(false);
      setRating(null);
      setSelectedAnswer(cards[currentCardIndex + 1].userAnswer);
    }
  };

  const handlePrevious = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(currentCardIndex - 1);
      setIsFlipped(false);
      setRating(null);
      setSelectedAnswer(cards[currentCardIndex - 1].userAnswer);
    }
  };

  const handleRating = (stars) => {
    setRating(stars);
  };

  const resetCards = () => {
    setCurrentCardIndex(0);
    setIsFlipped(false);
    setRating(null);
    setSelectedAnswer(null);
    setCards(mockFlashcards.map(card => ({ ...card, answered: false, userAnswer: null })));
  };

  const answeredCount = cards.filter(card => card.answered).length;
  const correctCount = cards.filter(card => card.answered && card.userAnswer === card.correctAnswer).length;

  const isCorrect = selectedAnswer === currentCard.correctAnswer;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">🎴 Financial Literacy Flashcard</h2>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">
            Score: {correctCount}/{answeredCount}
          </span>
          <button 
            onClick={resetCards}
            className="text-xs text-gray-400 hover:text-primary transition-colors flex items-center gap-1"
          >
            <RotateCw className="w-3 h-3" />
            Reset
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">
            Card {currentCardIndex + 1} of {cards.length}
          </span>
          <span className="text-sm text-gray-400">
            {answeredCount} completed
          </span>
        </div>
        <div className="w-full bg-dark-border rounded-full h-2">
          <div 
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        {/* Progress Dots */}
        <div className="flex items-center justify-center gap-2 mt-3">
          {cards.map((card, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentCardIndex
                  ? 'bg-primary w-3'
                  : card.answered
                  ? card.userAnswer === card.correctAnswer
                    ? 'bg-success'
                    : 'bg-red-500'
                  : 'bg-dark-border'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Flashcard */}
      <div className="mb-6">
        {!isFlipped ? (
          // Question Side with Multiple Choice
          <div className="space-y-4">
            <div className="bg-gradient-to-br from-primary/20 to-purple-600/20 border-2 border-primary/30 rounded-xl p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="text-3xl">❓</div>
                <p className="text-lg font-medium text-white leading-relaxed flex-1">
                  {currentCard.question}
                </p>
              </div>
            </div>

            {/* Multiple Choice Options */}
            <div className="space-y-3">
              {currentCard.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswerSelect(index)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedAnswer === index
                      ? 'border-primary bg-primary/20 scale-[1.02]'
                      : 'border-dark-border bg-dark-card hover:border-primary/50 hover:bg-dark-border/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                      selectedAnswer === index
                        ? 'border-primary bg-primary'
                        : 'border-gray-600'
                    }`}>
                      {selectedAnswer === index && (
                        <div className="w-3 h-3 bg-white rounded-full" />
                      )}
                    </div>
                    <span className="text-white font-medium">{option}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          // Answer Side
          <div className={`p-6 rounded-xl border-2 ${
            isCorrect
              ? 'bg-gradient-to-br from-success/20 to-emerald-600/20 border-success/30'
              : 'bg-gradient-to-br from-red-500/20 to-red-600/20 border-red-500/30'
          }`}>
            <div className="flex items-start gap-3 mb-4">
              <div className="text-3xl">
                {isCorrect ? '✅' : '❌'}
              </div>
              <div className="flex-1">
                <h3 className={`text-xl font-bold mb-2 ${
                  isCorrect ? 'text-success' : 'text-red-400'
                }`}>
                  {isCorrect ? 'Correct!' : 'Not quite!'}
                </h3>
                <p className="text-white mb-3">
                  The correct answer is: <span className="font-bold">{currentCard.options[currentCard.correctAnswer]}</span>
                </p>
                <p className="text-gray-300 leading-relaxed">
                  {currentCard.explanation}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={handlePrevious}
          disabled={currentCardIndex === 0}
          className="btn-secondary flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>

        {!isFlipped ? (
          <button
            onClick={handleRevealAnswer}
            disabled={selectedAnswer === null}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RotateCw className="w-4 h-4" />
            Check Answer
          </button>
        ) : (
          <button
            onClick={() => {
              setIsFlipped(false);
              setSelectedAnswer(null);
            }}
            className="btn-secondary flex items-center gap-2"
          >
            <RotateCw className="w-4 h-4" />
            Try Again
          </button>
        )}

        <button
          onClick={handleNext}
          disabled={currentCardIndex === cards.length - 1}
          className="btn-secondary flex items-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed"
        >
          Next
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Self-Assessment Rating */}
      {isFlipped && (
        <div className="border-t border-dark-border pt-4 animate-fadeIn">
          <p className="text-sm text-gray-400 text-center mb-3">
            How confident do you feel about this topic now?
          </p>
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3, 4, 5].map((stars) => (
              <button
                key={stars}
                onClick={() => handleRating(stars)}
                className={`p-2 rounded-lg transition-all ${
                  rating === stars
                    ? 'bg-warning/20 scale-110'
                    : 'hover:bg-dark-border'
                }`}
              >
                <Star
                  className={`w-6 h-6 ${
                    rating >= stars
                      ? 'fill-warning text-warning'
                      : 'text-gray-600'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}