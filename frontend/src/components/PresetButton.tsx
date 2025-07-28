import React from 'react';

interface PresetButtonProps {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
}

const PresetButton: React.FC<PresetButtonProps> = ({ label, onClick, icon }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className="px-4 py-2 bg-card border border-gray-700 rounded-full hover:bg-gray-700 transition-colors flex items-center gap-2 text-sm"
    >
      {icon && <span className="text-accent">{icon}</span>}
      <span>{label}</span>
    </button>
  );
};

export default PresetButton;