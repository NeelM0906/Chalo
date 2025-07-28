
import React from 'react';
import { GroundingChunk } from '../types';
import { LinkIcon } from './icons';

interface SourceListProps {
  sources: GroundingChunk[];
}

const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="max-w-3xl mx-auto mt-12 p-6 bg-card rounded-lg border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <LinkIcon className="w-5 h-5 text-accent" />
        Sources
      </h3>
      <p className="text-sm text-gray-400 mb-4">
        These itineraries were generated with the help of information from the following web pages:
      </p>
      <ul className="space-y-2">
        {sources.map((source, index) => (
          <li key={index}>
            <a 
              href={source.web.uri} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sm text-gray-300 hover:text-accent hover:underline truncate block"
              title={source.web.uri}
            >
              {source.web.title || source.web.uri}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SourceList;
