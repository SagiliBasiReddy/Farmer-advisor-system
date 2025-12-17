import { Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface QueryInputProps {
  query: string;
  setQuery: (query: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

const QueryInput = ({ query, setQuery, onSubmit, isLoading }: QueryInputProps) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !isLoading) {
        onSubmit();
      }
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <div className="card-agricultural p-6">
        {/* Label */}
        <label 
          htmlFor="query-input" 
          className="block text-sm font-medium text-muted-foreground mb-3"
        >
          Enter your farming question
        </label>

        {/* Text Input */}
        <Textarea
          id="query-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter farmer query in any language (Telugu, Tamil, Hindi, English...)"
          className="input-farm min-h-[120px] text-base resize-none mb-4"
          disabled={isLoading}
        />

        {/* Submit Button */}
        <Button
          onClick={onSubmit}
          disabled={!query.trim() || isLoading}
          className="btn-primary-farm w-full flex items-center justify-center gap-2 text-base"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Get Advice
            </>
          )}
        </Button>

        {/* Helper Text */}
        <p className="text-xs text-muted-foreground text-center mt-3">
          Press Enter to submit or Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default QueryInput;
