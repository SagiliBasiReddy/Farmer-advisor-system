import { useState } from "react";
import Header from "@/components/Header";
import QueryInput from "@/components/QueryInput";
import ResultsCard from "@/components/ResultsCard";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";

// Type definition for API response
interface Answer {
  text: string;
  confidence: number;
  rank: number;
}

interface AdvisoryResponse {
  translated: string;
  original_language?: string;
  original_language_advice?: string;
  canonical: string;
  advice: string;
  confidence: number;
  disclaimer: string;
  all_answers?: Answer[];
  answer_count?: number;
  is_validated?: boolean;
  validation_reason?: string;
}

const Index = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AdvisoryResponse | null>(null);
  const [error, setError] = useState(false);
  const [detectedLanguage, setDetectedLanguage] = useState<string>("");

  // Handle form submission
  const handleSubmit = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setResult(null);
    setError(false);

    try {
      // POST request to the Flask API
      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
      const response = await fetch(`${apiUrl}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          query: query.trim(),
          language: detectedLanguage // Pass detected language from transcription
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch advisory");
      }

      const data: AdvisoryResponse = await response.json();
      
      // Check if we got valid data
      if (data && data.advice) {
        setResult(data);
      } else {
        setError(true);
      }
    } catch (err) {
      console.error("Error fetching advisory:", err);
      setError(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle retry after error
  const handleRetry = () => {
    setError(false);
    setQuery("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Decorative animated background elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 right-0 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-teal-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 right-1/4 w-64 h-64 bg-green-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "0.5s" }} />
      </div>

      {/* Main content */}
      <div className="relative z-10">
        {/* Header */}
        <Header />

        {/* Main Content Area */}
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          {/* Query Input Section */}
          {!result && !error && (
            <div className="space-y-8">
              <QueryInput
                query={query}
                setQuery={setQuery}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                setDetectedLanguage={setDetectedLanguage}
              />
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-center items-center min-h-[400px]">
              <LoadingSpinner />
            </div>
          )}

          {/* Results */}
          {result && !isLoading && (
            <>
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <ResultsCard data={result} />
              </div>
              
              {/* Ask Another Question Button */}
              <div className="mt-12 text-center">
                <button
                  onClick={() => {
                    setResult(null);
                    setQuery("");
                    setDetectedLanguage("");
                  }}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-green-500/30 transition-all duration-200 hover:scale-105 active:scale-95"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Ask Another Question
                </button>
              </div>
            </>
          )}

          {/* Error State */}
          {error && !isLoading && <ErrorMessage onRetry={handleRetry} />}
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-gray-200/50 bg-white/50 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p className="text-center text-sm text-gray-600">
              🌾 AgroAdvisor • AI-Powered Agricultural Guidance for Modern Farmers
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Index;
