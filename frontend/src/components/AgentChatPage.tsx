import React, { useState } from 'react';
import React, { useState } from 'react';
import { AIEngineResponse, AIBusiness } from '../types';
import { getAgentRecommendations } from '../services/apiService';
import AgentInput from './AgentInput';
// Agent route components are not used with AI Engine response
import AgentLoadingState from './AgentLoadingState';
import { BrainIcon, MapPinIcon } from './icons';

const AgentChatPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentResponse, setAgentResponse] = useState<AIEngineResponse | null>(null);
  const [currentSearch, setCurrentSearch] = useState<{ userRequest: string; location: string } | null>(null);
  const [selectedBusiness, setSelectedBusiness] = useState<AIBusiness | null>(null);

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
      
      setAgentResponse(result);
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

  // No route selection/modal in AI Engine mode

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
          {/* Chat text summary */}
          {agentResponse.text && (
            <div className="bg-card border border-gray-700 rounded-2xl p-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-accent/20 text-accent rounded-full flex items-center justify-center">
                  <BrainIcon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-2">Suggested ideas</h3>
                  <p className="text-gray-300 whitespace-pre-line">{agentResponse.text}</p>
                </div>
              </div>
            </div>
          )}

          {/* Businesses */}
          {agentResponse.businesses && agentResponse.businesses.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6 text-center">
                Found {agentResponse.businesses.length} great places:
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agentResponse.businesses.map((biz: AIBusiness, index: number) => {
                  const gallery = (biz.phoos && biz.phoos.length > 0 ? biz.phoos : (biz.photos || [])) as string[];
                  const primary = gallery?.[0] || biz.image_url;
                  return (
                  <button
                    key={biz.id || index}
                    onClick={() => setSelectedBusiness(biz)}
                    className="text-left bg-card border border-gray-700 rounded-2xl overflow-hidden hover:border-accent transition-colors"
                  >
                    {primary && (
                      <img src={primary} alt={biz.name || 'Business'} className="w-full h-40 object-cover" />
                    )}
                    <div className="p-5 flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-white font-semibold text-lg mb-1">{biz.name}</h3>
                        {biz.location?.formatted_address && (
                          <p className="text-gray-400 text-sm">{biz.location.formatted_address}</p>
                        )}
                      </div>
                      {typeof biz.rating === 'number' && (
                        <div className="text-right">
                          <div className="text-accent font-bold">{biz.rating.toFixed(1)}</div>
                          {typeof biz.review_count === 'number' && (
                            <div className="text-gray-500 text-xs">{biz.review_count} reviews</div>
                          )}
                        </div>
                      )}
                    </div>
                    {gallery && gallery.length > 1 && (
                      <div className="px-5 pb-4 text-gray-400 text-xs">{gallery.length} photos</div>
                    )}
                    {biz.AboutThisBizSpecialties && (
                      <p className="px-5 pb-5 text-gray-300 text-sm">{biz.AboutThisBizSpecialties}</p>
                    )}
                    {biz.price && (
                      <div className="px-5 pb-5 -mt-2 text-gray-400 text-sm">Price: {biz.price}</div>
                    )}
                  </button>
                )})}
              </div>
            </div>
          )}

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

      {/* Business detail modal */}
      {selectedBusiness && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-card border border-gray-700 rounded-2xl max-w-2xl w-full overflow-hidden">
            {/* Header image */}
            {(() => {
              const gallery = (selectedBusiness.phoos && selectedBusiness.phoos.length > 0 ? selectedBusiness.phoos : (selectedBusiness.photos || [])) as string[];
              const primary = gallery?.[0] || selectedBusiness.image_url;
              return primary ? (
                <img src={primary} alt={selectedBusiness.name || 'Business'} className="w-full h-56 object-cover" />
              ) : null;
            })()}
            <div className="p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-2xl font-bold text-white mb-1">{selectedBusiness.name}</h3>
                  {selectedBusiness.location?.formatted_address && (
                    <p className="text-gray-400">{selectedBusiness.location.formatted_address}</p>
                  )}
                </div>
                <button
                  onClick={() => setSelectedBusiness(null)}
                  className="text-gray-400 hover:text-white"
                  aria-label="Close"
                >
                  ✕
                </button>
              </div>

              <div className="mt-4 flex items-center gap-4 text-sm text-gray-300">
                {typeof selectedBusiness.rating === 'number' && (
                  <span className="text-accent font-semibold">Rating: {selectedBusiness.rating.toFixed(1)}</span>
                )}
                {typeof selectedBusiness.review_count === 'number' && (
                  <span>{selectedBusiness.review_count} reviews</span>
                )}
                {selectedBusiness.price && <span>Price: {selectedBusiness.price}</span>}
              </div>

              {/* About sections */}
              <div className="mt-6 space-y-3 text-gray-300 text-sm">
                {selectedBusiness.AboutThisBizBio && (
                  <p><span className="text-gray-400">About:</span> {selectedBusiness.AboutThisBizBio}</p>
                )}
                {selectedBusiness.AboutThisBizSpecialties && (
                  <p><span className="text-gray-400">Specialties:</span> {selectedBusiness.AboutThisBizSpecialties}</p>
                )}
                {selectedBusiness.AboutThisBizHistory && (
                  <p><span className="text-gray-400">History:</span> {selectedBusiness.AboutThisBizHistory}</p>
                )}
                {selectedBusiness.AboutThisBizYearEstablished && (
                  <p><span className="text-gray-400">Established:</span> {selectedBusiness.AboutThisBizYearEstablished}</p>
                )}
              </div>

              {/* Photos gallery */}
              {(() => {
                const gallery = (selectedBusiness.phoos && selectedBusiness.phoos.length > 0 ? selectedBusiness.phoos : (selectedBusiness.photos || [])) as string[];
                if (gallery && gallery.length > 1) {
                  return (
                    <div className="mt-6 grid grid-cols-3 gap-2">
                      {gallery.slice(0, 6).map((url, idx) => (
                        <img key={idx} src={url} alt={`Photo ${idx + 1}`} className="w-full h-24 object-cover rounded" />
                      ))}
                    </div>
                  );
                }
                return null;
              })()}

              {/* Full details (keeps users on our app) */}
              <div className="mt-6 border-t border-gray-700 pt-4">
                <h4 className="text-white font-semibold mb-3">Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm text-gray-300">
                  {selectedBusiness.location?.address1 && (
                    <div><span className="text-gray-400">Address 1:</span> {selectedBusiness.location.address1}</div>
                  )}
                  {selectedBusiness.location?.address2 && (
                    <div><span className="text-gray-400">Address 2:</span> {selectedBusiness.location.address2}</div>
                  )}
                  {selectedBusiness.location?.city && (
                    <div><span className="text-gray-400">City:</span> {selectedBusiness.location.city}</div>
                  )}
                  {selectedBusiness.location?.state && (
                    <div><span className="text-gray-400">State:</span> {selectedBusiness.location.state}</div>
                  )}
                  {selectedBusiness.location?.zip_code && (
                    <div><span className="text-gray-400">Zip Code:</span> {selectedBusiness.location.zip_code}</div>
                  )}
                  {/* Hiding country and formatted address per request */}
                  {(selectedBusiness.coordinates?.lat !== undefined || selectedBusiness.coordinates?.lng !== undefined) && (
                    <div className="md:col-span-2">
                      <span className="text-gray-400">Coordinates:</span> {selectedBusiness.coordinates?.lat ?? '—'}, {selectedBusiness.coordinates?.lng ?? '—'}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentChatPage;