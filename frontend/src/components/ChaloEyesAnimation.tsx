import React from 'react';

interface ChaloEyesAnimationProps {
  size?: number;
  className?: string;
}

const ChaloEyesAnimation: React.FC<ChaloEyesAnimationProps> = ({ 
  size = 48, 
  className = "" 
}) => {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div 
        className="relative flex items-center gap-3"
        style={{ width: size * 2.2, height: size }}
      >
        {/* Left Eye */}
        <div 
          className="relative bg-white rounded-full border-2 border-accent/30 shadow-lg"
          style={{ width: size * 0.9, height: size * 0.9 }}
        >
          <div 
            className="absolute bg-accent rounded-full"
            style={{ 
              width: size * 0.35, 
              height: size * 0.35,
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              animation: 'chalo-left 3s ease-in-out infinite'
            }}
          >
            <div 
              className="absolute bg-primary rounded-full"
              style={{ 
                width: size * 0.18, 
                height: size * 0.18,
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)'
              }}
            />
          </div>
        </div>

        {/* Right Eye */}
        <div 
          className="relative bg-white rounded-full border-2 border-accent/30 shadow-lg"
          style={{ width: size * 0.9, height: size * 0.9 }}
        >
          <div 
            className="absolute bg-accent rounded-full"
            style={{ 
              width: size * 0.35, 
              height: size * 0.35,
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              animation: 'chalo-right 3s ease-in-out infinite'
            }}
          >
            <div 
              className="absolute bg-primary rounded-full"
              style={{ 
                width: size * 0.18, 
                height: size * 0.18,
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)'
              }}
            />
          </div>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes chalo-left {
          0% { transform: translate(-50%, -50%); }
          20% { transform: translate(-30%, -50%); }
          40% { transform: translate(-70%, -50%); }
          60% { transform: translate(-50%, -30%); }
          80% { transform: translate(-50%, -70%); }
          100% { transform: translate(-50%, -50%); }
        }
        
        @keyframes chalo-right {
          0% { transform: translate(-50%, -50%); }
          25% { transform: translate(-70%, -50%); }
          50% { transform: translate(-30%, -50%); }
          75% { transform: translate(-50%, -70%); }
          100% { transform: translate(-50%, -50%); }
        }
      `}</style>
    </div>
  );
};

export default ChaloEyesAnimation;