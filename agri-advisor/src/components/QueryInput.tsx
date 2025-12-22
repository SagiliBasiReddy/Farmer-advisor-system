import { useState, useEffect, useRef } from "react";
import { Send, Loader2, Mic, MicOff } from "lucide-react";

interface QueryInputProps {
  query: string;
  setQuery: (query: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  setDetectedLanguage?: (language: string) => void;
}

const QueryInput = ({ query, setQuery, onSubmit, isLoading, setDetectedLanguage: setParentLanguage }: QueryInputProps) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [detectedLanguage, setDetectedLanguage] = useState<string>("");
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check for browser support for Web Speech API
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setIsSupported(true);
      const recognition = new SpeechRecognition();
      
      // Configure for multi-language support
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = ""; // Auto-detect by default
      
      recognition.onstart = () => {
        setIsListening(true);
        setDetectedLanguage("Listening...");
      };
      
      recognition.onresult = (event: any) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptSegment = event.results[i][0].transcript;
          transcript += transcriptSegment;
        }
        
        setQuery(transcript);
        
        // Detect language when we have enough text
        if (transcript.length > 10) {
          detectLanguageFromText(transcript);
        }
        
        // If this is the final result, make sure language detection completes
        if (event.results[event.results.length - 1].isFinal) {
          // Give API a moment to complete language detection
          setTimeout(() => {
            if (transcript.length > 10) {
              detectLanguageFromText(transcript);
            }
          }, 300);
        }
      };
      
      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
        if (event.error === "no-speech") {
          setDetectedLanguage("No speech detected. Please try again.");
        } else if (event.error === "not-allowed") {
          setDetectedLanguage("Microphone permission denied.");
        } else {
          setDetectedLanguage(`Error: ${event.error}`);
        }
      };
      
      recognition.onend = () => {
        setIsListening(false);
        // Clear "Listening..." message after speech ends, but keep detected language
        setTimeout(() => {
          setDetectedLanguage((prev) => prev === "Listening..." ? "" : prev);
        }, 500);
      };
      
      recognitionRef.current = recognition;
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const detectLanguageFromText = (text: string) => {
    // Send text to backend for accurate language detection
    if (!text || text.length < 3) return;
    
    const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
    
    fetch(`${apiUrl}/detect-language`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setDetectedLanguage(data.language_name);
          if (setParentLanguage) {
            setParentLanguage(data.language_name);
          }
          console.log(`[DETECT] Language: ${data.language_name} (${data.language_code})`);
        }
      })
      .catch(err => {
        console.error("Language detection error:", err);
      });
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        setQuery(""); // Clear previous query
        recognitionRef.current.start();
      } catch (e) {
        console.error("Error starting recognition:", e);
        setDetectedLanguage("Error starting microphone");
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      setDetectedLanguage(""); // Clear the listening message
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !isLoading) {
        onSubmit();
      }
    }
  };

  return (
    <div className="w-full">
      <div className="relative bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 rounded-3xl shadow-2xl shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all duration-300 p-6 sm:p-8 border border-emerald-500/20">
        {/* Animated border glow */}
        <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity" style={{
          background: 'radial-gradient(circle at top right, rgba(16, 185, 129, 0.1), transparent)',
        }} />

        {/* Header */}
        <div className="mb-6 relative z-10">
          <h2 className="text-3xl font-black text-emerald-100 mb-2">
            🌾 Ask Your Farming Question
          </h2>
          <p className="text-emerald-200/70 text-sm font-medium">
            Speak or type in any language — Telugu, Tamil, Hindi, Marathi, English, or any Indian language
          </p>
        </div>

        {/* Textarea with Mic Button */}
        <div className="relative mb-4 group">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your crops, pests, fertilizers, irrigation, or any farming problem..."
            className="relative z-10 w-full min-h-[140px] p-5 border-2 border-emerald-500/30 rounded-2xl text-base text-emerald-50 placeholder-emerald-200/40 resize-none focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/30 transition-all duration-200 bg-slate-900/50 backdrop-blur-sm"
            disabled={isLoading}
          />
          
          {/* Mic Button */}
          {isSupported && (
            <button
              type="button"
              onClick={isListening ? stopListening : startListening}
              disabled={isLoading}
              className={`absolute bottom-4 right-4 p-3 rounded-full transition-all duration-200 z-20 ${
                isListening
                  ? "bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/50 animate-pulse"
                  : "bg-gradient-to-br from-emerald-400 to-teal-500 hover:from-emerald-300 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/50 hover:shadow-emerald-500/70"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={isListening ? "Stop recording" : "Start voice input"}
            >
              {isListening ? (
                <MicOff className="w-5 h-5" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>
          )}
        </div>

        {/* Language Detection Indicator */}
        {detectedLanguage && (
          <div className="mb-4 inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-900/40 to-emerald-900/40 text-emerald-200 rounded-full text-sm font-bold border border-emerald-500/30 backdrop-blur-sm">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            🌍 {detectedLanguage}
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={onSubmit}
          disabled={!query.trim() || isLoading || isListening}
          className="relative w-full py-4 bg-gradient-to-r from-emerald-500 via-teal-500 to-green-500 text-white font-bold rounded-2xl text-lg flex items-center justify-center gap-2 hover:shadow-2xl hover:shadow-emerald-500/50 transition-all duration-200 hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 active:scale-95 overflow-hidden group"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 opacity-0 group-hover:opacity-20 transition-opacity" />
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin relative z-10" />
              <span className="relative z-10">Processing your query...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5 relative z-10" />
              <span className="relative z-10">Get Advice</span>
            </>
          )}
        </button>

        {/* Helper Text */}
        <p className="text-xs text-emerald-200/50 text-center mt-4 font-medium">
          💡 Tip: Press <kbd className="bg-slate-700/50 px-2 py-1 rounded text-emerald-200 font-mono border border-emerald-500/20">Enter</kbd> to submit, 
          <kbd className="bg-slate-700/50 px-2 py-1 rounded text-emerald-200 font-mono ml-1 border border-emerald-500/20">Shift+Enter</kbd> for new line
        </p>
      </div>
    </div>
  );
};

export default QueryInput;
