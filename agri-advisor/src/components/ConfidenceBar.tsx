interface ConfidenceBarProps {
  confidence: number;
}

const ConfidenceBar = ({ confidence }: ConfidenceBarProps) => {
  const percentage = Math.round(confidence * 100);
  
  // Determine color based on confidence level
  const getConfidenceClass = () => {
    if (confidence >= 0.7) return "confidence-high";
    if (confidence >= 0.4) return "confidence-medium";
    return "confidence-low";
  };

  const getConfidenceLabel = () => {
    if (confidence >= 0.7) return "High Confidence";
    if (confidence >= 0.4) return "Moderate Confidence";
    return "Low Confidence";
  };

  return (
    <div className="space-y-2">
      {/* Header with percentage and label */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">
          {getConfidenceLabel()}
        </span>
        <span className="text-lg font-bold text-foreground">
          {percentage}%
        </span>
      </div>

      {/* Progress Bar Background */}
      <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
        {/* Animated Fill */}
        <div
          className={`confidence-bar ${getConfidenceClass()}`}
          style={{
            width: `${percentage}%`,
            transition: "width 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
        />
      </div>
    </div>
  );
};

export default ConfidenceBar;
