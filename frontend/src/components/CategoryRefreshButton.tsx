import React from 'react';
import { RefreshIcon } from './icons';

interface CategoryRefreshButtonProps {
  onClick: (e: React.MouseEvent) => void;
  isLoading: boolean;
  size?: 'sm' | 'md';
  disabled?: boolean;
}

const CategoryRefreshButton: React.FC<CategoryRefreshButtonProps> = ({ 
  onClick, 
  isLoading, 
  size = 'sm',
  disabled = false 
}) => {
  const sizeClasses = {
    sm: 'p-2 w-8 h-8',
    md: 'p-3 w-10 h-10'
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`
        ${sizeClasses[size]}
        rounded-full 
        bg-purple-600/40 
        hover:bg-purple-600/60 
        disabled:bg-gray-600/40 
        disabled:cursor-not-allowed
        transition-all 
        duration-200 
        flex 
        items-center 
        justify-center
        border
        border-purple-500/30
        hover:border-purple-400/50
        disabled:border-gray-500/30
      `}
      aria-label={isLoading ? 'Refreshing category...' : 'Refresh with different category'}
      title="Get a spot from a different category"
    >
      <RefreshIcon 
        className={`
          ${iconSizes[size]} 
          ${isLoading ? 'animate-spin text-purple-300' : 'text-purple-200'}
          ${disabled ? 'text-gray-400' : ''}
          transition-colors
          duration-200
        `} 
      />
    </button>
  );
};

export default CategoryRefreshButton;