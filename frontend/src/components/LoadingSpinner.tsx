
import React from 'react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex flex-col justify-center items-center py-16">
      <svg
        width="80"
        height="40"
        viewBox="0 0 80 40"
        className="text-accent"
        xmlns="http://www.w3.org/2000/svg"
      >
        <g className="eye-group">
          {/* Left Eye */}
          <path
            d="M5 20 C 5 11.7, 11.7 5, 20 5 S 35 11.7, 35 20 S 28.3 35, 20 35 S 5 28.3, 5 20"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          />
          <circle className="pupil" cx="20" cy="20" r="5" fill="currentColor" />

          {/* Right Eye */}
          <path
            d="M45 20 C 45 11.7, 51.7 5, 60 5 S 75 11.7, 75 20 S 68.3 35, 60 35 S 45 28.3, 45 20"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          />
          <circle className="pupil" cx="60" cy="20" r="5" fill="currentColor" />
        </g>
      </svg>
      <style>{`
        .pupil {
          animation: look-around 4s ease-in-out infinite;
        }
        @keyframes look-around {
          0% { transform: translateX(0px) translateY(0px); }
          15% { transform: translateX(5px) translateY(0px); } /* look right */
          30% { transform: translateX(5px) translateY(0px); }
          45% { transform: translateX(-5px) translateY(0px); } /* look left */
          60% { transform: translateX(-5px) translateY(0px); }
          75% { transform: translateX(0px) translateY(0px); } /* look center */
          85% { transform: translateX(0px) translateY(-4px); } /* look up */
          95% { transform: translateX(0px) translateY(0px); } /* look center */
          100% { transform: translateX(0px) translateY(0px); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
