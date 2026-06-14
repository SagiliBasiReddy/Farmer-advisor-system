import { Sprout } from "lucide-react";

const LoadingSpinner = () => {
  return (
    <div className="w-full flex items-center justify-center py-16">
      <div className="text-center space-y-8">
        {/* Animated Icon Container */}
        <div className="relative w-32 h-32 mx-auto">
          {/* Outer rotating ring */}
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-emerald-400 border-r-teal-400 animate-spin shadow-2xl shadow-emerald-500/50" />
          
          {/* Middle rotating ring (slower) */}
          <div 
            className="absolute inset-3 rounded-full border-4 border-transparent border-b-teal-500 border-l-emerald-500 shadow-lg shadow-teal-500/30"
            style={{
              animation: "spin 3s linear infinite reverse"
            }}
          />
          
          {/* Center icon - pulsing */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative">
              <Sprout className="w-12 h-12 text-emerald-400 animate-bounce drop-shadow-lg" />
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full blur-xl opacity-50 -z-10 animate-pulse" />
            </div>
          </div>
        </div>

        {/* Text Content */}
        <div className="space-y-3">
          <p className="text-2xl font-black text-emerald-100">
            🔍 Analyzing your question...
          </p>
          <p className="text-emerald-200/70 text-base font-medium">
            Finding the best agricultural advice for your farming needs
          </p>
        </div>

        {/* Animated dots */}
        <div className="flex justify-center items-center gap-3">
          <div className="w-3 h-3 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full animate-bounce shadow-lg shadow-emerald-500/50" style={{ animationDelay: "0s" }} />
          <div className="w-3 h-3 bg-gradient-to-br from-teal-400 to-cyan-500 rounded-full animate-bounce shadow-lg shadow-teal-500/50" style={{ animationDelay: "0.2s" }} />
          <div className="w-3 h-3 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full animate-bounce shadow-lg shadow-green-500/50" style={{ animationDelay: "0.4s" }} />
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
