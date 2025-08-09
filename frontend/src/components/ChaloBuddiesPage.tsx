import React from 'react';
import { Itinerary, Stop } from '../types';
import { MapPinIcon, ClockIcon, WalkIcon, UsersIcon } from './icons';

// A curated list of high-quality, generic stock images to cycle through for the mock data.
const STOCK_IMAGE_URLS = [
  'https://images.unsplash.com/photo-1541167760496-1628856ab772?q=80&w=1637&auto=format&fit=crop', // Coffee latte art
  'https://images.unsplash.com/photo-1472851294608-062f824d29cc?q=80&w=1470&auto=format&fit=crop', // Boutique shop
  'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=1374&auto=format&fit=crop', // Plated food
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1470&auto=format&fit=crop', // Restaurant interior
  'https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1469&auto=format&fit=crop', // Modern museum
  'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=1544&auto=format&fit=crop', // Cityscape
];

// Define a new type for the curated path to include the author
interface CuratedPath extends Itinerary {
    author: {
        name: string;
        avatarUrl?: string; // Optional avatar
    };
    location: string;
}

// Mock data for Mini's curated path in Mumbai
const curatedPaths: CuratedPath[] = [
    {
        id: 'friend-path-mumbai-mini-1',
        author: { name: 'Mini' },
        title: "Mini's Mumbai Munch & Shop",
        location: "Mumbai, India",
        description: "A perfect day out in South Mumbai, combining delicious treats with some bargain hunting and a classic cafe experience.",
        duration_minutes: 190,
        stops: [
            {
                id: 'stop-mumbai-1',
                name: 'Theobroma',
                category: 'Patisserie & Cafe',
                walking_time_minutes: 0, // First stop
                description: 'Start your day with their iconic brownies and a cup of coffee at this beloved local bakery chain.',
                image_url: STOCK_IMAGE_URLS[0],
            },
            {
                id: 'stop-mumbai-2',
                name: 'Fashion Street',
                category: 'Street Market',
                walking_time_minutes: 15,
                description: 'Hunt for trendy clothes, accessories, and footwear at this bustling open-air market known for bargains.',
                image_url: STOCK_IMAGE_URLS[1],
            },
            {
                id: 'stop-mumbai-3',
                name: 'Mondegar Cafe',
                category: 'Restaurant & Bar',
                walking_time_minutes: 10,
                description: 'End your adventure with delicious pasta and tunes from the jukebox at this legendary, art-filled Mumbai cafe.',
                image_url: STOCK_IMAGE_URLS[2],
            }
        ]
    }
];

// --- Stop Component for the Curated Path Card ---
const PathStopItem: React.FC<{ stop: Stop; isLast: boolean; location: string }> = ({ stop, isLast, location }) => {
    const mapsQuery = encodeURIComponent(`${stop.name}, ${location}`);
    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${mapsQuery}`;

    return (
        <div className="relative pl-12 pb-12">
            {/* Vertical connector line */}
            {!isLast && <div className="absolute top-5 left-5 -ml-px h-full w-0.5 bg-gray-600 border border-dashed border-gray-600"></div>}
            
            {/* Stop Icon */}
            <div className="absolute top-0 left-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-card border-2 border-accent">
                    <MapPinIcon className="w-5 h-5 text-accent"/>
                </div>
            </div>

            {/* Stop Details */}
            <div className="flex flex-col md:flex-row gap-6">
                <div className="w-full md:w-48 flex-shrink-0">
                     <img src={stop.image_url} alt={stop.name} className="w-full h-32 object-cover rounded-md border border-gray-600" />
                </div>
                <div className="flex-grow">
                    <h4 className="font-bold text-lg text-white">
                        <a href={mapsUrl} target="_blank" rel="noopener noreferrer" className="hover:underline hover:text-accent transition-colors duration-200">
                            {stop.name}
                        </a>
                    </h4>
                    <p className="text-sm text-accent font-semibold mb-2">{stop.category}</p>
                    <p className="text-gray-300 text-sm">{stop.description}</p>
                </div>
            </div>
            
            {/* Walking time to next stop */}
            {!isLast && (
                <div className="flex items-center gap-2 mt-6 ml-[-5px] text-gray-400">
                    <WalkIcon className="w-4 h-4" />
                    <span>{stop.walking_time_minutes} min walk to next stop</span>
                </div>
            )}
        </div>
    );
};


// --- Card component to display a friend's curated path ---
const FriendPathCard: React.FC<{ path: CuratedPath }> = ({ path }) => {
    return (
        <div className="bg-card rounded-xl border border-gray-700 overflow-hidden">
            <div className="p-6 bg-secondary border-b border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                            <UsersIcon className="w-6 h-6 text-accent"/>
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Curated by</p>
                            <p className="font-bold text-white">{path.author.name}</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="font-bold text-white">{path.location}</p>
                        <p className="text-sm text-gray-400">Location</p>
                    </div>
                </div>
                <h3 className="text-2xl font-bold tracking-tight text-white mt-6">{path.title}</h3>
                <p className="text-gray-300 mt-2 max-w-3xl">{path.description}</p>
            </div>
            <div className="p-6">
                {path.stops.map((stop, index) => (
                    <PathStopItem key={stop.id} stop={stop} isLast={index === path.stops.length - 1} location={path.location} />
                ))}
            </div>
             <div className="flex items-center justify-between text-sm text-gray-300 border-t border-gray-700 p-6 bg-secondary">
                <div className="flex items-center gap-2">
                    <ClockIcon className="w-5 h-5 text-accent" />
                    <span>Total Duration: ~{Math.round(path.duration_minutes / 60 * 10) / 10} hours</span>
                </div>
                <div className="flex items-center gap-2">
                    <MapPinIcon className="w-5 h-5 text-accent" />
                    <span>{path.stops.length} stops</span>
                </div>
            </div>
        </div>
    )
};


// --- Main Chalo Buddies Page Component ---
const ChaloBuddiesPage: React.FC = () => {
    return (
        <div>
            <div className="mb-12 text-center">
                <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white">
                    Chalo Buddies
                </h1>
                <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mt-4">
                    Explore hand-picked adventures curated by your friends.
                </p>
            </div>

            <div className="max-w-4xl mx-auto space-y-8">
                {curatedPaths.map(path => (
                    <FriendPathCard key={path.id} path={path} />
                ))}
            </div>
        </div>
    );
};

export default ChaloBuddiesPage;