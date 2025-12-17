import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorMessageProps {
  onRetry: () => void;
}

const ErrorMessage = ({ onRetry }: ErrorMessageProps) => {
  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <div className="card-agricultural p-8 text-center animate-fade-up">
        {/* Icon */}
        <div className="w-16 h-16 mx-auto mb-4 bg-destructive/10 rounded-full flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-destructive" />
        </div>

        {/* Message */}
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Unable to Find Advisory
        </h3>
        <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
          We couldn't find a suitable advisory for your query. Please try rephrasing your question or ask about a different topic.
        </p>

        {/* Retry Button */}
        <Button
          onClick={onRetry}
          variant="outline"
          className="gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Try Again
        </Button>
      </div>
    </div>
  );
};

export default ErrorMessage;
