import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorMessageProps {
  onRetry: () => void;
}

const ErrorMessage = ({ onRetry }: ErrorMessageProps) => {
  return (
    <div className="w-full flex items-center justify-center py-12">
      <div className="relative bg-gradient-to-br from-red-900 via-red-800 to-slate-900 rounded-3xl border-2 border-red-500/50 shadow-2xl shadow-red-500/30 p-10 max-w-md text-center animate-in fade-in slide-in-from-bottom-4 duration-500 overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-br from-red-400/10 to-transparent opacity-0 hover:opacity-100 transition-opacity" />
        
        {/* Icon */}
        <div className="relative z-10 w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-red-400 to-red-600 rounded-full flex items-center justify-center shadow-2xl shadow-red-500/50">
          <AlertCircle className="w-10 h-10 text-white" />
        </div>

        {/* Message */}
        <h3 className="relative z-10 text-2xl font-black text-red-100 mb-3">
          ⚠️ Something Went Wrong
        </h3>
        <p className="relative z-10 text-red-200/80 mb-8 text-base leading-relaxed font-medium">
          We couldn't find a suitable advisory for your query. Please try rephrasing your question or ask about a different farming topic.
        </p>

        {/* Retry Button */}
        <button
          onClick={onRetry}
          className="relative z-10 inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-red-500 via-red-600 to-red-700 text-white font-bold rounded-xl hover:shadow-2xl hover:shadow-red-500/50 transition-all duration-200 hover:scale-110 active:scale-95"
        >
          <RefreshCw className="w-5 h-5" />
          Try Again
        </button>
      </div>
    </div>
  );
};

export default ErrorMessage;
