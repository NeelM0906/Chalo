import React from 'react';

interface FilterDropdownsProps {
  priceFilter: string;
  distanceFilter: number;
  onPriceChange: (price: string) => void;
  onDistanceChange: (distance: number) => void;
  isLoading: boolean;
}

const FilterDropdowns: React.FC<FilterDropdownsProps> = ({
  priceFilter,
  distanceFilter,
  onPriceChange,
  onDistanceChange,
  isLoading
}) => {
  const priceOptions = [
    { value: '', label: 'Any Price' },
    { value: '10-20', label: '$10-20' },
    { value: '20-50', label: '$20-50' },
    { value: '50+', label: '$50+' }
  ];

  const distanceOptions = [
    { value: 0.5, label: '0.5 miles' },
    { value: 1, label: '1 mile' },
    { value: 1.5, label: '1.5 miles' },
    { value: 2, label: '2 miles' },
    { value: 2.5, label: '2.5 miles' },
    { value: 3, label: '3 miles' },
    { value: 5, label: '5 miles' }
  ];

  return (
    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-4">
      <div className="flex flex-col">
        <label htmlFor="price-filter" className="text-sm text-gray-400 mb-1">
          Price Range
        </label>
        <select
          id="price-filter"
          value={priceFilter}
          onChange={(e) => onPriceChange(e.target.value)}
          disabled={isLoading}
          className="px-4 py-2 bg-secondary border border-gray-600 rounded-lg text-white focus:outline-none focus:border-accent disabled:opacity-50 disabled:cursor-not-allowed min-w-[120px]"
        >
          {priceOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col">
        <label htmlFor="distance-filter" className="text-sm text-gray-400 mb-1">
          Search Distance
        </label>
        <select
          id="distance-filter"
          value={distanceFilter}
          onChange={(e) => onDistanceChange(Number(e.target.value))}
          disabled={isLoading}
          className="px-4 py-2 bg-secondary border border-gray-600 rounded-lg text-white focus:outline-none focus:border-accent disabled:opacity-50 disabled:cursor-not-allowed min-w-[120px]"
        >
          {distanceOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FilterDropdowns;