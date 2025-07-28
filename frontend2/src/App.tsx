import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { MapPin, Sparkles, Clock, DollarSign, Star, RefreshCw, Zap, Heart } from 'lucide-react'
import Typewriter from './components/fancy/Typewriter'
import ScrambleHover from './components/fancy/ScrambleHover'
import { getItineraries, refreshSpot, healthCheck } from './services/apiService'
import { Itinerary, Stop } from './types'
import './App.css'

function App() {
  const [location, setLocation] = useState('')
  const [preset, setPreset] = useState('')
  const [itineraries, setItineraries] = useState<Itinerary[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isHealthy, setIsHealthy] = useState(false)

  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await healthCheck()
      setIsHealthy(healthy)
    }
    
    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!location.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await getItineraries(location, preset || undefined)
      setItineraries(response.itineraries)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleRefreshSpot = async (itineraryIndex: number, stopIndex: number) => {
    const itinerary = itineraries[itineraryIndex]
    const stop = itinerary.stops[stopIndex]
    
    try {
      const excludedIds = itinerary.stops.map(s => s.id)
      const newSpot = await refreshSpot(location, stop.category, excludedIds)
      
      const updatedItineraries = [...itineraries]
      updatedItineraries[itineraryIndex].stops[stopIndex] = newSpot
      setItineraries(updatedItineraries)
    } catch (err) {
      console.error('Failed to refresh spot:', err)
    }
  }

  const presetOptions = [
    { value: 'foodie', label: '🍕 Foodie Adventure', color: 'from-orange-400 to-red-500' },
    { value: 'culture', label: '🎨 Cultural Explorer', color: 'from-purple-400 to-indigo-500' },
    { value: 'nature', label: '🌿 Nature Lover', color: 'from-green-400 to-emerald-500' },
    { value: 'nightlife', label: '🌙 Nightlife', color: 'from-blue-400 to-purple-500' },
    { value: 'family', label: '👨‍👩‍👧‍👦 Family Fun', color: 'from-yellow-400 to-orange-500' },
    { value: 'budget', label: '💰 Budget Friendly', color: 'from-teal-400 to-cyan-500' },
    { value: 'luxury', label: '✨ Luxury Experience', color: 'from-pink-400 to-rose-500' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Subtle background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-32 h-32 bg-purple-500/5 rounded-full blur-xl animate-pulse-slow" />
        <div className="absolute top-40 right-32 w-24 h-24 bg-blue-500/5 rounded-full blur-xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-32 left-1/3 w-40 h-40 bg-indigo-500/5 rounded-full blur-xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div 
          className="text-center mb-12"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="relative inline-block">
            <h1 className="text-5xl md:text-6xl font-black text-white mb-4 relative">
              <Typewriter 
                text={["LocalWander", "Discover", "Explore", "Adventure"]}
                speed={80}
                waitTime={2500}
                className="bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent"
              />
              <motion.div 
                className="absolute -top-2 -right-8 text-2xl"
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              >
                ✨
              </motion.div>
            </h1>
          </div>
          
          <motion.p 
            className="text-xl text-gray-300 max-w-2xl mx-auto mb-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <ScrambleHover 
              text="Discover amazing local experiences with AI-powered itineraries"
              className="text-gray-300"
              scrambledClassName="text-purple-400"
            />
          </motion.p>

          {/* Health Status with fun styling */}
          <motion.div 
            className="flex items-center justify-center gap-2 mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            <motion.div 
              className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-green-400' : 'bg-red-400'}`}
              animate={isHealthy ? { scale: [1, 1.2, 1] } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span className="text-sm text-gray-400 font-medium">
              Backend {isHealthy ? 'Connected' : 'Disconnected'}
            </span>
            {isHealthy && <Zap className="w-4 h-4 text-green-400" />}
          </motion.div>
        </motion.div>

        {/* Search Form */}
        <motion.div 
          className="max-w-3xl mx-auto mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Location Input */}
            <div className="relative group">
              <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 group-focus-within:text-purple-400 transition-colors" />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter a location (e.g., Manhattan, NY)"
                className="w-full pl-12 pr-4 py-4 bg-white/10 backdrop-blur-md border-2 border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-purple-400 transition-all duration-300 hover:border-white/30"
                required
              />
            </div>
            
            {/* Preset Buttons */}
            <div className="space-y-3">
              <p className="text-gray-300 font-medium flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                Choose your vibe (optional):
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {presetOptions.map((option) => (
                  <motion.button
                    key={option.value}
                    type="button"
                    onClick={() => setPreset(preset === option.value ? '' : option.value)}
                    className={`p-3 rounded-xl border-2 transition-all duration-300 text-sm font-medium ${
                      preset === option.value
                        ? `bg-gradient-to-r ${option.color} text-white border-transparent shadow-lg`
                        : 'bg-white/5 text-gray-300 border-white/20 hover:border-white/40 hover:bg-white/10'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {option.label}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white font-bold rounded-2xl hover:from-purple-600 hover:via-pink-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl relative overflow-hidden"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.div 
                    key="loading"
                    className="flex items-center justify-center gap-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Generating Itineraries...
                  </motion.div>
                ) : (
                  <motion.span
                    key="generate"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    🚀 Generate Itineraries
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          </form>
        </motion.div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div 
              className="max-w-2xl mx-auto mb-8 p-4 bg-red-500/20 border-2 border-red-500/30 rounded-2xl text-red-300 backdrop-blur-md"
              initial={{ opacity: 0, scale: 0.9, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex items-center gap-2">
                <span className="text-xl">⚠️</span>
                <span>{error}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Itineraries */}
        <AnimatePresence>
          {itineraries.length > 0 && (
            <motion.div 
              className="space-y-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <motion.div 
                className="text-center mb-8"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <h2 className="text-3xl font-bold text-white mb-2">
                  🎯 Your Adventures Await!
                </h2>
                <p className="text-gray-400">
                  Generated for: <span className="font-semibold text-purple-400">{location}</span>
                  {preset && <span className="text-gray-500"> • {presetOptions.find(p => p.value === preset)?.label}</span>}
                </p>
              </motion.div>

              <div className="grid gap-8">
                {itineraries.map((itinerary, itineraryIndex) => (
                  <motion.div 
                    key={itinerary.id}
                    className="bg-white/10 backdrop-blur-md border-2 border-white/20 rounded-3xl p-8 hover:bg-white/15 hover:border-white/30 transition-all duration-300 group"
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: itineraryIndex * 0.1, duration: 0.6 }}
                    whileHover={{ y: -5 }}
                  >
                    <div className="mb-6">
                      <h3 className="text-2xl md:text-3xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors">
                        <ScrambleHover 
                          text={itinerary.title}
                          className="text-white group-hover:text-purple-300"
                          scrambledClassName="text-purple-400"
                        />
                      </h3>
                      <p className="text-gray-300 mb-4 text-lg">{itinerary.description}</p>
                      
                      <div className="flex flex-wrap gap-4 text-sm">
                        <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full">
                          <Clock className="w-4 h-4" />
                          {itinerary.duration}
                        </div>
                        {itinerary.total_walking_time && (
                          <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 text-green-300 rounded-full">
                            <MapPin className="w-4 h-4" />
                            {itinerary.total_walking_time} walking
                          </div>
                        )}
                        {itinerary.estimated_cost && (
                          <div className="flex items-center gap-2 px-3 py-1 bg-yellow-500/20 text-yellow-300 rounded-full">
                            <DollarSign className="w-4 h-4" />
                            {itinerary.estimated_cost}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="grid gap-4">
                      {itinerary.stops.map((stop, stopIndex) => (
                        <motion.div 
                          key={stop.id}
                          className="bg-white/5 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300 border border-white/10 hover:border-white/20"
                          whileHover={{ x: 5 }}
                        >
                          <div className="flex justify-between items-start mb-3">
                            <h4 className="text-xl font-semibold text-white">
                              {stop.name}
                            </h4>
                            <motion.button
                              onClick={() => handleRefreshSpot(itineraryIndex, stopIndex)}
                              className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full transition-all duration-200"
                              whileHover={{ rotate: 180, scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                            >
                              <RefreshCw className="w-4 h-4" />
                            </motion.button>
                          </div>
                          
                          <p className="text-gray-300 mb-4">{stop.description}</p>
                          
                          <div className="flex flex-wrap gap-3 text-sm">
                            <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full font-medium">
                              {stop.category}
                            </span>
                            {stop.rating && (
                              <div className="flex items-center gap-1 px-3 py-1 bg-yellow-500/20 text-yellow-300 rounded-full">
                                <Star className="w-4 h-4 fill-current" />
                                {stop.rating}
                              </div>
                            )}
                            {stop.price_level && (
                              <div className="flex items-center gap-1 px-3 py-1 bg-green-500/20 text-green-300 rounded-full">
                                <DollarSign className="w-4 h-4" />
                                {'$'.repeat(stop.price_level)}
                              </div>
                            )}
                          </div>
                          
                          {stop.address && (
                            <p className="text-gray-500 text-sm mt-3 italic">{stop.address}</p>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default App