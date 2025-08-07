import React, { useState } from 'react';
import { AgentResponse, AgentRoute } from '../types';
import { getAgentRecommendations } from '../services/apiService';
import AgentInput from './AgentInput';
import AgentRouteCard from './AgentRouteCard';
import AgentRouteModal from './AgentRouteModal';
import AgentLoadingState from './AgentLoadingState';
import { BrainIcon, MapPinIcon } from './icons';

const AgentChatPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentResponse, setAgentResponse] = useState<AgentResponse | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<AgentRoute | null>(null);
  const [currentSearch, setCurrentSearch] = useState<{ userRequest: string; location: string } | null>(null);

  const handleSearch = async (userRequest: string, location: string, distanceMiles: number) => {
    setIsLoading(true);
    setError(null);
    setAgentResponse(null);
    setCurrentSearch({ userRequest, location });

    try {
      // Add minimum delay for better UX
      const minDelay = new Promise(resolve => setTimeout(resolve, 3000));
      const apiCall = getAgentRecommendations(userRequest, location, distanceMiles);
      
      const [result] = await Promise.all([apiCall, minDelay]);
      
      if (result.recommendations?.routes && result.recommendations.routes.length > 0) {
        setAgentResponse(result);
      } else {
        setError('I couldn\'t find any great routes for your request. Try different keywords or expand your search area.');
      }
    } catch (e) {
      console.error('Agent search error:', e);
      if (e instanceof Error) {
        if (e.message.includes('Unable to connect to the server')) {
          setError('Unable to connect to the AI agent. Please ensure the backend server is running on port 8000.');
        } else {
          setError(e.message);
        }
      } else {
        setError('Something went wrong while finding your adventure. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRouteSelect = (route: AgentRoute) => {
    setSelectedRoute(route);
  };

  const handleCloseModal = () => {
    setSelectedRoute(null);
  };

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    window.location.hash = '#/';
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex justify-center items-center gap-3 mb-4">
          <BrainIcon className="w-12 h-12 text-accent" />
          <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white">
            AI Adventure Guide
          </h1>
        </div>
        <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto">
          Tell me what you're craving, and I'll craft the perfect local adventure just for you.
        </p>
      </div>

      {/* Input Section */}
      <div className="mb-12">
        <AgentInput onSearch={handleSearch} isLoading={isLoading} />
      </div>

      {/* Loading State */}
      {isLoading && currentSearch && (
        <AgentLoadingState 
          userRequest={currentSearch.userRequest}
          location={currentSearch.location}
        />
      )}

      {/* Error State */}
      {error && (
        <div className="text-center py-12">
          <div className="bg-red-900/20 border border-red-700/50 rounded-2xl p-8 max-w-2xl mx-auto">
            <p className="text-red-400 text-lg mb-4">{error}</p>
            <p className="text-gray-400 text-sm">
              Try rephrasing your request or check your location spelling.
            </p>
          </div>
        </div>
      )}

      {/* Results Section */}
      {!isLoading && agentResponse && (
        <div className="space-y-8">
          {/* User Intent Summary */}
          <div className="bg-card border border-gray-700 rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-accent/20 text-accent rounded-full flex items-center justify-center">
                <BrainIcon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <h3 className="text-white font-semibold mb-2">I understand you're looking for:</h3>
                <p className="text-gray-300 mb-3">"{agentResponse.user_intent.mood_context}"</p>
                <div className="flex flex-wrap gap-2">
                  {agentResponse.user_intent.search_queries.map((query, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-accent/10 text-accent rounded-full text-sm font-medium"
                    >
                      {query}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Routes */}
          <div>
            <h2 className="text-2xl font-bold text-white mb-6 text-center">
              Here are {agentResponse.recommendations.routes.length} perfect routes for you:
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {agentResponse.recommendations.routes.map((route, index) => (
                <AgentRouteCard
                  key={index}
                  route={route}
                  onSelect={handleRouteSelect}
                />
              ))}
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center py-8">
            <p className="text-gray-400 mb-4">
              Want to explore more traditional itineraries?
            </p>
            <a 
              href="#/" 
              onClick={handleNavClick}
              className="inline-flex items-center gap-2 px-6 py-3 bg-secondary hover:bg-card text-white font-semibold rounded-xl transition-colors"
            >
              <MapPinIcon className="w-5 h-5" />
              Browse Regular Itineraries
            </a>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && !agentResponse && (
        <div className="text-center py-16">
          <div className="bg-card border border-gray-700 rounded-2xl p-12 max-w-2xl mx-auto">
            <BrainIcon className="w-16 h-16 text-gray-500 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-white mb-4">
              Ready to discover your next adventure?
            </h3>
            <p className="text-gray-400 leading-relaxed">
              I'm here to help you find the perfect local experience. Just tell me what you're in the mood for, 
              and I'll create a personalized route with insider tips and local favorites.
            </p>
          </div>
        </div>
      )}

      {/* Route Detail Modal */}
      {selectedRoute && (
        <AgentRouteModal
          route={selectedRoute}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default AgentChatPage;