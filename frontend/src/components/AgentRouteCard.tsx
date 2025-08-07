import React from 'react';
import { AgentRoute } from '../types';
import { ClockIcon, WalkIcon, MapPinIcon } from './icons';

interface AgentRouteCardProps {
  route: AgentRoute;
  onSelect: (route: AgentRoute) => void;
}

const AgentRouteCard: React.FC<AgentRouteCardProps> = ({ route, onSelect }) => {
  const totalWalkingTime = route.stops.reduce((sum, stop) => sum + stop.walking_time_to_next, 0);

  return (
    <div 
      className="bg-card rounded-2xl border border-gray-700 hover:border-accent/50 transition-all duration-300 cursor-pointer group hover:shadow-xl hover:shadow-accent/10 transform hover:scale-[1.02]"
      onClick={() => onSelect(route)}
    >
      {/* Header */}
      <div className="p-6 pb-4">
        <h3 className="text-xl font-bold text-white mb-2 group-hover:text-accent transition-colors">
          {route.name}
        </h3>
        <p className="text-gray-300 leading-relaxed">
          {route.description}
        </p>
      </div>

      {/* Stats */}
      <div className="px-6 pb-4">
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <div className="flex items-center gap-1">
            <MapPinIcon className="w-4 h-4" />
            <span>{route.stops.length} stops</span>
          </div>
          <div className="flex items-center gap-1">
            <ClockIcon className="w-4 h-4" />
            <span>{route.total_duration_minutes} min</span>
          </div>
          <div className="flex items-center gap-1">
            <WalkIcon className="w-4 h-4" />
            <span>{totalWalkingTime} min walk</span>
          </div>
        </div>
      </div>

      {/* Stops Preview */}
      <div className="px-6 pb-4">
        <div className="space-y-3">
          {route.stops.slice(0, 3).map((stop, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="flex-shrink-0 w-6 h-6 bg-accent/20 text-accent rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-white truncate">
                    {stop.place_name}
                  </h4>
                  <span className="text-xs text-accent bg-accent/10 px-2 py-0.5 rounded-full flex-shrink-0">
                    {stop.category}
                  </span>
                </div>
                <p className="text-sm text-gray-400 line-clamp-2">
                  {stop.why_recommended}
                </p>
                {stop.walking_time_to_next > 0 && (
                  <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                    <WalkIcon className="w-3 h-3" />
                    <span>{stop.walking_time_to_next} min to next</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {route.stops.length > 3 && (
            <div className="text-center text-sm text-gray-400 pt-2">
              +{route.stops.length - 3} more stops
            </div>
          )}
        </div>
      </div>

      {/* Local Tip */}
      {route.local_tip && (
        <div className="px-6 pb-6">
          <div className="bg-accent/10 border border-accent/20 rounded-xl p-4">
            <div className="flex items-start gap-2">
              <span className="text-accent text-lg">💡</span>
              <div>
                <h5 className="text-accent font-semibold text-sm mb-1">Local Tip</h5>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {route.local_tip}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Hint */}
      <div className="px-6 pb-6">
        <div className="text-center">
          <span className="text-xs text-gray-500 group-hover:text-accent transition-colors">
            Click to view full route details
          </span>
        </div>
      </div>
    </div>
  );
};

export default AgentRouteCard;