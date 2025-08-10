import React from 'react';
import { AIDayPlan } from '../types';
import { ClockIcon, MapPinIcon, WalkIcon, LinkIcon, BrainIcon, LogoIcon } from './icons';
import AIPlanMapEmbed from './AIPlanMapEmbed';

interface AIDayPlanCardProps {
  plan: AIDayPlan;
}

const formatDuration = (minutes?: number) => {
  if (!minutes || minutes <= 0) return null;
  if (minutes < 60) return `${minutes} min`;
  const hrs = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins === 0 ? `${hrs} hr` : `${hrs} hr ${mins} min`;
};

const AIDayPlanCard: React.FC<AIDayPlanCardProps> = ({ plan }) => {
  const totalStops = plan.total_stops ?? plan.stops?.length ?? 0;
  const coverImage = plan.stops?.find(s => !!s.image_url)?.image_url;
  const enrichedStops = plan.stops || [];

  return (
    <div className="bg-card rounded-2xl border border-gray-700 overflow-hidden">
      {/* Cover */}
      <div className="w-full h-48 bg-secondary flex items-center justify-center overflow-hidden">
        {coverImage ? (
          <img src={coverImage} alt={plan.title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-800">
            <LogoIcon className="w-16 h-16 text-gray-600" />
          </div>
        )}
      </div>

      {/* Header */}
      <div className="p-6">
        <div className="flex items-start gap-3 mb-2">
          <div className="flex-shrink-0 w-10 h-10 bg-accent/20 text-accent rounded-full flex items-center justify-center">
            <BrainIcon className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-1">{plan.title}</h3>
            {plan.summary && (
              <p className="text-gray-300 leading-relaxed">{plan.summary}</p>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-300 mt-3">
          {plan.total_duration_minutes !== undefined && (
            <div className="flex items-center gap-2">
              <ClockIcon className="w-4 h-4 text-accent" />
              <span>{formatDuration(plan.total_duration_minutes)}</span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <MapPinIcon className="w-4 h-4 text-accent" />
            <span>{totalStops} stops</span>
          </div>
          {plan.start_time && plan.end_time && (
            <div className="text-gray-400">{plan.start_time} - {plan.end_time}</div>
          )}
          {/* Hide broken short links; use embedded route below instead */}
        </div>
      </div>

      {/* Stops */}
      {Array.isArray(plan.stops) && plan.stops.length > 0 && (
        <div className="px-6 pb-6">
          <div className="space-y-4">
            {enrichedStops.map((stop, idx) => (
              <div key={`${stop.name}-${idx}`} className="bg-secondary/30 border border-gray-700 rounded-xl overflow-hidden">
                <div className="flex">
                  {/* Image */}
                  <div className="w-28 h-28 flex-shrink-0 bg-secondary overflow-hidden">
                    {stop.image_url ? (
                      <img src={stop.image_url} alt={stop.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gray-800">
                        <LogoIcon className="w-10 h-10 text-gray-600" />
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="bg-accent/20 text-accent text-xs font-bold px-2 py-0.5 rounded">
                            Stop {idx + 1}
                          </span>
                          {stop.category && (
                            <span className="text-xs text-gray-400 uppercase tracking-wide">{stop.category}</span>
                          )}
                          {stop.time && (
                            <span className="text-xs text-gray-400">{stop.time}</span>
                          )}
                        </div>
                        <h4 className="font-semibold text-white text-base">{stop.name}</h4>
                        {stop.address && (
                          <p className="text-gray-400 text-sm mt-0.5">{stop.address}</p>
                        )}
                        <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-gray-400">
                          {typeof stop.rating === 'number' && (
                            <span className="text-accent font-semibold">{stop.rating.toFixed(1)} ★</span>
                          )}
                          {stop.price && (
                            <span>Price: {stop.price}</span>
                          )}
                          {stop.lat !== undefined && stop.lng !== undefined && (
                            <span>({stop.lat}, {stop.lng})</span>
                          )}
                          {stop.url && (
                            <a href={stop.url} target="_blank" rel="noreferrer" className="text-accent hover:underline">Open</a>
                          )}
                        </div>
                      </div>
                      {stop.duration_minutes && stop.duration_minutes > 0 && (
                        <div className="flex items-center gap-1 text-xs text-gray-400">
                          <ClockIcon className="w-3.5 h-3.5 text-accent" />
                          <span>{formatDuration(stop.duration_minutes)}</span>
                        </div>
                      )}
                    </div>

                    {stop.notes && (
                      <p className="text-gray-300 text-sm mt-2">{stop.notes}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Embedded route map */}
      {Array.isArray(plan.stops) && plan.stops.length >= 2 && (
        <div className="px-6">
          <AIPlanMapEmbed stops={plan.stops} />
        </div>
      )}

      {/* Tips / Extras */}
      {(plan.tips && plan.tips.length > 0) || plan.budget || plan.transportation || plan.weather_note ? (
        <div className="px-6 pb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plan.tips && plan.tips.length > 0 && (
              <div className="bg-accent/10 border border-accent/20 rounded-xl p-4">
                <h5 className="text-accent font-semibold mb-2 text-sm">Tips</h5>
                <ul className="list-disc list-inside text-gray-300 text-sm space-y-1">
                  {plan.tips.map((tip, i) => (
                    <li key={i}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}
            {(plan.budget || plan.transportation || plan.weather_note) && (
              <div className="bg-secondary/30 border border-gray-700 rounded-xl p-4 space-y-2">
                {plan.budget && (
                  <div className="text-gray-300 text-sm"><span className="text-gray-400">Budget:</span> {plan.budget}</div>
                )}
                {plan.transportation && (
                  <div className="text-gray-300 text-sm"><span className="text-gray-400">Transport:</span> {plan.transportation}</div>
                )}
                {plan.weather_note && (
                  <div className="text-gray-300 text-sm"><span className="text-gray-400">Weather:</span> {plan.weather_note}</div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default AIDayPlanCard;
