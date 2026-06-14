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
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [detectedLanguage, setDetectedLanguage] = useState<string>("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setDetectedLanguage("Starting microphone...");
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        } 
      });
      
      streamRef.current = stream;
      audioChunksRef.current = [];

      // Create MediaRecorder with appropriate MIME type
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/wav';

      const mediaRecorder = new MediaRecorder(stream, { 
        mimeType,
        audioBitsPerSecond: 128000 
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());

        if (audioChunksRef.current.length === 0) {
          setDetectedLanguage("No audio recorded. Please try again.");
          return;
        }

        // Convert audio chunks to WAV format
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        
        // Send to backend for transcription via Sarvam
        await transcribeAudio(audioBlob);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setDetectedLanguage("Recording... Click to stop");
      setQuery(""); // Clear previous query
    } catch (err: any) {
      console.error("Error starting recording:", err);
      if (err.name === "NotAllowedError") {
        setDetectedLanguage("Microphone permission denied");
      } else if (err.name === "NotFoundError") {
        setDetectedLanguage("No microphone found");
      } else {
        setDetectedLanguage(`Error: ${err.message}`);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      setIsTranscribing(true);
      setDetectedLanguage("Transcribing with Sarvam...");

      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.wav");

      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
      
      const response = await fetch(`${apiUrl}/transcribe`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Transcription failed");
      }

      // Set the transcribed text
      setQuery(result.transcribed_text);
      
      // Set detected language
      if (result.language_name) {
        setDetectedLanguage(`🌍 ${result.language_name}`);
        if (setParentLanguage) {
          setParentLanguage(result.language_name);
        }
      }

      console.log(`[TRANSCRIBE] Success: ${result.transcribed_text}`);
    } catch (err: any) {
      console.error("Transcription error:", err);
      setDetectedLanguage(`Error: ${err.message}`);
    } finally {
      setIsTranscribing(false);
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
          <button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading || isTranscribing}
            className={`absolute bottom-4 right-4 p-3 rounded-full transition-all duration-200 z-20 ${
              isRecording
                ? "bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/50 animate-pulse"
                : "bg-gradient-to-br from-emerald-400 to-teal-500 hover:from-emerald-300 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/50 hover:shadow-emerald-500/70"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title={isRecording ? "Stop recording" : "Start voice recording"}
          >
            {isRecording ? (
              <MicOff className="w-5 h-5" />
            ) : (
              <Mic className="w-5 h-5" />
            )}
          </button>
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
          disabled={!query.trim() || isLoading || isRecording || isTranscribing}
          className="relative w-full py-4 bg-gradient-to-r from-emerald-500 via-teal-500 to-green-500 text-white font-bold rounded-2xl text-lg flex items-center justify-center gap-2 hover:shadow-2xl hover:shadow-emerald-500/50 transition-all duration-200 hover:scale-105 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 active:scale-95 overflow-hidden group"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 opacity-0 group-hover:opacity-20 transition-opacity" />
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin relative z-10" />
              <span className="relative z-10">Processing your query...</span>
            </>
          ) : isTranscribing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin relative z-10" />
              <span className="relative z-10">Transcribing...</span>
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
