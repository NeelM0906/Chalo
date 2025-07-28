import React from 'react';
import { RefreshIcon } from './icons';

interface RefreshButtonProps {
  onClick: () => void;
  isLoading: boolean;
  size?: 'sm' | 'md';
}

const RefreshButton: React.FC<RefreshButtonProps> = ({ 
  onClick, 
  isLoading,
  size = 'md'
}) => {
  const sizeClasses = size === 'sm' ? 'w-6 h-6 p-1' : 'w-8 h-8 p-1.5';
  
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`${sizeClasses} rounded-full bg-accent/20 hover:bg-accent/30 
                 text-accent transition-colors flex items-center justify-center
                 disabled:opacity-50 disabled:cursor-not-allowed`}
      title="Find alternative spot"
    >
      <RefreshIcon className={`${isLoading ? 'animate-spin' : ''} w-full h-full`} />
    </button>
  );
};

export default RefreshButton;