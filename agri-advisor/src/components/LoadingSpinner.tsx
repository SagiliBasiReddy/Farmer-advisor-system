import { Loader2, Sprout } from "lucide-react";

const LoadingSpinner = () => {
  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <div className="card-agricultural p-12 text-center">
        {/* Animated Icon */}
        <div className="relative w-20 h-20 mx-auto mb-6">
          {/* Spinning ring */}
          <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
          <div className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin" />
          
          {/* Center icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <Sprout className="w-8 h-8 text-primary animate-pulse-soft" />
          </div>
        </div>

        {/* Text */}
        <p className="text-lg font-medium text-foreground mb-2">
          Analyzing your query...
        </p>
        <p className="text-sm text-muted-foreground">
          Finding the best agricultural advice for you
        </p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
