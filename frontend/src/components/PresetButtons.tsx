import React from 'react';
import { TreeIcon, PaletteIcon, UtensilsIcon, LandmarkIcon, ShoppingBagIcon } from './icons';
import PresetButton from './PresetButton';

interface PresetButtonsProps {
  onPresetSearch: (preset: string) => void;
  isLoading: boolean;
}

const PresetButtons: React.FC<PresetButtonsProps> = ({ onPresetSearch, isLoading }) => {
  return (
    <div className="flex flex-wrap gap-2 justify-center mt-6">
      <PresetButton 
        label="Nature & Parks" 
        onClick={() => !isLoading && onPresetSearch("Nature & Parks")} 
        icon={<TreeIcon className="w-4 h-4" />} 
      />
      <PresetButton 
        label="Art & Culture" 
        onClick={() => !isLoading && onPresetSearch("Art & Culture")} 
        icon={<PaletteIcon className="w-4 h-4" />} 
      />
      <PresetButton 
        label="Foodie Delights" 
        onClick={() => !isLoading && onPresetSearch("Foodie Delights")} 
        icon={<UtensilsIcon className="w-4 h-4" />} 
      />
      <PresetButton 
        label="Historical Landmarks" 
        onClick={() => !isLoading && onPresetSearch("Historical Landmarks")} 
        icon={<LandmarkIcon className="w-4 h-4" />} 
      />
      <PresetButton 
        label="Shopping & Boutiques" 
        onClick={() => !isLoading && onPresetSearch("Shopping & Boutiques")} 
        icon={<ShoppingBagIcon className="w-4 h-4" />} 
      />
    </div>
  );
};

export default PresetButtons;