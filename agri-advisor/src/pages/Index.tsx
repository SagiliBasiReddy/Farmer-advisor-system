import { useState } from "react";
import Header from "@/components/Header";
import QueryInput from "@/components/QueryInput";
import ResultsCard from "@/components/ResultsCard";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorMessage from "@/components/ErrorMessage";

// Type definition for API response
interface AdvisoryResponse {
  translated: string;
  canonical: string;
  advice: string;
  confidence: number;
  disclaimer: string;
}

const Index = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AdvisoryResponse | null>(null);
  const [error, setError] = useState(false);

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
        body: JSON.stringify({ query: query.trim() }),
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
    <div className="min-h-screen bg-background">
      {/* Decorative background pattern */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-30"
        style={{
          backgroundImage: `radial-gradient(circle at 20% 80%, hsl(var(--primary) / 0.08) 0%, transparent 50%),
                           radial-gradient(circle at 80% 20%, hsl(var(--accent) / 0.08) 0%, transparent 50%)`,
        }}
      />

      {/* Main content */}
      <div className="relative z-10 pb-16">
        {/* Header */}
        <Header />

        {/* Main Content Area */}
        <main className="mt-8 space-y-8">
          {/* Query Input - Always visible unless showing results */}
          {!result && !error && (
            <QueryInput
              query={query}
              setQuery={setQuery}
              onSubmit={handleSubmit}
              isLoading={isLoading}
            />
          )}

          {/* Loading State */}
          {isLoading && <LoadingSpinner />}

          {/* Results */}
          {result && !isLoading && (
            <>
              <ResultsCard data={result} />
              
              {/* Ask Another Question Button */}
              <div className="text-center mt-8">
                <button
                  onClick={() => {
                    setResult(null);
                    setQuery("");
                  }}
                  className="text-primary hover:text-primary/80 font-medium underline underline-offset-4 transition-colors"
                >
                  Ask another question
                </button>
              </div>
            </>
          )}

          {/* Error State */}
          {error && !isLoading && <ErrorMessage onRetry={handleRetry} />}
        </main>
      </div>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 py-4 bg-background/80 backdrop-blur-sm border-t border-border">
        <p className="text-center text-sm text-muted-foreground">
          Farmer Advisory System • Academic Demo
        </p>
      </footer>
    </div>
  );
};

export default Index;
