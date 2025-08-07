import React, { useState } from 'react';
import { MessageCircleIcon } from './icons';

interface AgentInputProps {
  onSearch: (userRequest: string, location: string, distanceMiles: number) => void;
  isLoading: boolean;
}

const AgentInput: React.FC<AgentInputProps> = ({ onSearch, isLoading }) => {
  const [userRequest, setUserRequest] = useState('');
  const [location, setLocation] = useState('');
  const [distanceMiles, setDistanceMiles] = useState(1.5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userRequest.trim() && location.trim()) {
      onSearch(userRequest.trim(), location.trim(), distanceMiles);
    }
  };

  const isValid = userRequest.trim().length >= 3 && location.trim().length >= 2;

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Request Input */}
        <div className="relative">
          <textarea
            value={userRequest}
            onChange={(e) => setUserRequest(e.target.value)}
            placeholder="What you in the mood for?"
            className="w-full px-6 py-4 text-lg bg-card border border-gray-600 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent resize-none transition-all duration-200"
            rows={3}
            disabled={isLoading}
            maxLength={200}
          />
          <div className="absolute bottom-3 right-3 text-xs text-gray-500">
            {userRequest.length}/200
          </div>
        </div>

        {/* Location and Distance Row */}
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-gray-300 text-lg font-medium">in</span>
          
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="San Francisco, CA"
              className="w-full px-4 py-3 text-lg bg-card border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all duration-200"
              disabled={isLoading}
            />
          </div>

          <span className="text-gray-300 text-lg font-medium">within</span>
          
          <div className="flex items-center gap-2">
            <input
              type="range"
              min="0.5"
              max="5"
              step="0.5"
              value={distanceMiles}
              onChange={(e) => setDistanceMiles(parseFloat(e.target.value))}
              className="w-20 accent-accent"
              disabled={isLoading}
            />
            <span className="text-accent font-semibold min-w-[60px]">
              {distanceMiles} mi
            </span>
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={!isValid || isLoading}
            className="inline-flex items-center gap-3 px-8 py-4 bg-accent hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 text-lg shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
          >
            <MessageCircleIcon className="w-5 h-5" />
            {isLoading ? 'Finding Your Adventure...' : 'Find My Adventure'}
          </button>
        </div>

        {/* Input Hints */}
        {!isLoading && (
          <div className="text-center space-y-2">
            <p className="text-gray-400 text-sm">
              Try: "thai food and something sweet" or "coffee and a walk in the park"
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                "chinese food and activities",
                "sushi and desserts", 
                "mexican food and museums",
                "coffee and shopping"
              ].map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => setUserRequest(example)}
                  className="px-3 py-1 text-xs bg-secondary hover:bg-card text-gray-300 hover:text-white rounded-full transition-colors duration-200"
                  disabled={isLoading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default AgentInput;