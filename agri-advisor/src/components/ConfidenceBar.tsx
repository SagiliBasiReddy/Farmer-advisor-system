interface ConfidenceBarProps {
  confidence: number;
}

const ConfidenceBar = ({ confidence }: ConfidenceBarProps) => {
  const percentage = Math.round(confidence * 100);
  
  // Determine color based on confidence level
  const getGradient = () => {
    if (confidence >= 0.7) return "bg-gradient-to-r from-emerald-400 via-teal-500 to-emerald-600 shadow-lg shadow-emerald-500/50";
    if (confidence >= 0.4) return "bg-gradient-to-r from-amber-400 via-orange-500 to-amber-600 shadow-lg shadow-amber-500/50";
    return "bg-gradient-to-r from-red-400 via-rose-500 to-red-600 shadow-lg shadow-red-500/50";
  };

  const getLabel = () => {
    if (confidence >= 0.7) return "High Confidence";
    if (confidence >= 0.4) return "Moderate Confidence";
    return "Low Confidence";
  };

  const getColor = () => {
    if (confidence >= 0.7) return "text-emerald-300";
    if (confidence >= 0.4) return "text-amber-300";
    return "text-red-300";
  };

  return (
    <div className="space-y-3">
      {/* Progress Bar */}
      <div className="w-full h-4 bg-slate-700/50 rounded-full overflow-hidden shadow-inner border border-slate-600/50">
        {/* Animated Fill with gradient */}
        <div
          className={`h-full ${getGradient()} rounded-full shadow-md`}
          style={{
            width: `${percentage}%`,
            transition: "width 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
            boxShadow: "0 0 10px rgba(0,0,0,0.1)"
          }}
        />
      </div>
      
      {/* Label and percentage */}
      <div className="flex items-center justify-between">
        <span className={`text-sm font-semibold ${getColor()}`}>
          {getLabel()}
        </span>
        <span className={`text-lg font-bold ${getColor()}`}>
          {percentage}%
        </span>
      </div>
    </div>
  );
};

export default ConfidenceBar;
