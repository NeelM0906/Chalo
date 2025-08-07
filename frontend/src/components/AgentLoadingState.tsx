import React from 'react';
import { BrainIcon } from './icons';

interface AgentLoadingStateProps {
  userRequest: string;
  location: string;
}

const AgentLoadingState: React.FC<AgentLoadingStateProps> = ({ userRequest, location }) => {
  const loadingMessages = [
    "Understanding your cravings...",
    "Exploring local favorites...",
    "Crafting your perfect route...",
    "Adding local insights...",
    "Almost ready with your adventure!"
  ];

  const [currentMessageIndex, setCurrentMessageIndex] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessageIndex((prev) => (prev + 1) % loadingMessages.length);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6">
      {/* Animated Brain Icon */}
      <div className="relative mb-8">
        <div className="animate-pulse">
          <BrainIcon className="w-16 h-16 text-accent" />
        </div>
        <div className="absolute inset-0 animate-ping">
          <BrainIcon className="w-16 h-16 text-accent/30" />
        </div>
      </div>

      {/* User Request Echo */}
      <div className="bg-card border border-gray-700 rounded-2xl p-6 mb-6 max-w-md w-full">
        <div className="text-center">
          <p className="text-gray-400 text-sm mb-2">You're looking for:</p>
          <p className="text-white font-semibold text-lg mb-1">"{userRequest}"</p>
          <p className="text-accent text-sm">in {location}</p>
        </div>
      </div>

      {/* Loading Message */}
      <div className="text-center">
        <p className="text-xl text-white font-medium mb-2 transition-all duration-500">
          {loadingMessages[currentMessageIndex]}
        </p>
        <p className="text-gray-400">
          Our AI is curating the perfect local experience for you
        </p>
      </div>

      {/* Progress Dots */}
      <div className="flex gap-2 mt-6">
        {[0, 1, 2].map((dot) => (
          <div
            key={dot}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              (currentMessageIndex + dot) % 3 === 0 
                ? 'bg-accent scale-125' 
                : 'bg-gray-600'
            }`}
          />
        ))}
      </div>
    </div>
  );
};

export default AgentLoadingState;