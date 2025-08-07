import React from 'react';
import { AgentRoute } from '../types';
import { XIcon, ClockIcon, WalkIcon, MapPinIcon } from './icons';

interface AgentRouteModalProps {
  route: AgentRoute;
  onClose: () => void;
}

const AgentRouteModal: React.FC<AgentRouteModalProps> = ({ route, onClose }) => {
  const totalWalkingTime = route.stops.reduce((sum, stop) => sum + stop.walking_time_to_next, 0);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-primary border border-gray-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">
              {route.name}
            </h2>
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-1">
                <MapPinIcon className="w-4 h-4" />
                <span>{route.stops.length} stops</span>
              </div>
              <div className="flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                <span>{route.total_duration_minutes} min total</span>
              </div>
              <div className="flex items-center gap-1">
                <WalkIcon className="w-4 h-4" />
                <span>{totalWalkingTime} min walking</span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-card rounded-full transition-colors"
            aria-label="Close modal"
          >
            <XIcon className="w-6 h-6 text-gray-400 hover:text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Description */}
          <div className="p-6 border-b border-gray-700">
            <p className="text-gray-300 leading-relaxed">
              {route.description}
            </p>
          </div>

          {/* Stops */}
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Your Route</h3>
            <div className="space-y-4">
              {route.stops.map((stop, index) => (
                <div key={index} className="relative">
                  <div className="flex items-start gap-4">
                    {/* Step Number */}
                    <div className="flex-shrink-0 w-8 h-8 bg-accent text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    
                    {/* Stop Details */}
                    <div className="flex-1 min-w-0">
                      <div className="bg-card rounded-xl p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-white">
                            {stop.place_name}
                          </h4>
                          <span className="text-xs text-accent bg-accent/10 px-2 py-1 rounded-full">
                            {stop.category}
                          </span>
                        </div>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {stop.why_recommended}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Walking Time to Next */}
                  {stop.walking_time_to_next > 0 && index < route.stops.length - 1 && (
                    <div className="flex items-center gap-2 mt-3 ml-4 pl-4">
                      <div className="w-px h-6 bg-gray-600"></div>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <WalkIcon className="w-4 h-4" />
                        <span>{stop.walking_time_to_next} minute walk</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Local Tip */}
          {route.local_tip && (
            <div className="p-6 border-t border-gray-700">
              <div className="bg-accent/10 border border-accent/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <span className="text-accent text-2xl">💡</span>
                  <div>
                    <h4 className="text-accent font-semibold mb-2">Local Insider Tip</h4>
                    <p className="text-gray-300 leading-relaxed">
                      {route.local_tip}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 bg-secondary/50">
          <div className="flex justify-center">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-accent hover:bg-blue-600 text-white font-semibold rounded-xl transition-colors"
            >
              Got it, let's go!
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentRouteModal;