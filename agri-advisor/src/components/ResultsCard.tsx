import { Lightbulb, AlertTriangle, CheckCircle2, AlertCircle, TrendingUp, Zap } from "lucide-react";
import ConfidenceBar from "./ConfidenceBar";

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
  audio_base64?: string;
  audio_language?: string;
  has_audio?: boolean;
}

interface ResultsCardProps {
  data: AdvisoryResponse;
}

const ResultsCard = ({ data }: ResultsCardProps) => {
  const hasOriginalLanguage = data.original_language && data.original_language !== "English";
  const confidencePercentage = Math.round(data.confidence * 100);
  
  return (
    <div className="w-full space-y-8">
      {/* Main Advice - Dual Language Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* English Advice - Emerald Card */}
        <div className="group relative bg-gradient-to-br from-emerald-900 via-teal-900 to-slate-900 rounded-3xl border-2 border-emerald-500/50 shadow-2xl shadow-emerald-500/30 hover:shadow-emerald-500/50 p-8 hover:scale-105 transition-all duration-300 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-400/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="relative z-10">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-4 bg-gradient-to-br from-emerald-400 to-teal-600 rounded-2xl shadow-lg shadow-emerald-500/50 group-hover:scale-110 transition-transform">
                <Lightbulb className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-emerald-100">Recommended Action</h2>
                <p className="text-xs text-emerald-300 font-bold mt-1">🇬🇧 English</p>
              </div>
            </div>
            <p className="text-emerald-50 text-lg leading-relaxed font-semibold">
              {data.advice}
            </p>
          </div>
        </div>

        {/* Original Language Advice - Teal Card */}
        {hasOriginalLanguage ? (
          <div className="group relative bg-gradient-to-br from-teal-900 via-cyan-900 to-slate-900 rounded-3xl border-2 border-teal-500/50 shadow-2xl shadow-teal-500/30 hover:shadow-teal-500/50 p-8 hover:scale-105 transition-all duration-300 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-teal-400/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative z-10">
              <div className="flex items-start gap-4 mb-6">
                <div className="p-4 bg-gradient-to-br from-teal-400 to-cyan-600 rounded-2xl shadow-lg shadow-teal-500/50 group-hover:scale-110 transition-transform">
                  <Lightbulb className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-teal-100">📍 {data.original_language}</h2>
                  <p className="text-xs text-teal-300 font-bold mt-1">Your Language</p>
                </div>
              </div>
              <p className="text-teal-50 text-lg leading-relaxed font-semibold">
                {data.original_language_advice || data.advice}
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl border-2 border-slate-700/50 shadow-xl p-8 opacity-50">
            <div className="flex items-center justify-center h-full">
              <p className="text-slate-400 text-center font-medium">English query - same advice shown</p>
            </div>
          </div>
        )}
      </div>

      {/* Audio Player Section */}
      {data.has_audio && data.audio_base64 && (
        <div className="bg-gradient-to-br from-violet-900 via-purple-900 to-slate-900 rounded-3xl border-2 border-violet-500/50 shadow-2xl shadow-violet-500/30 p-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-4 bg-gradient-to-br from-violet-400 to-purple-600 rounded-2xl shadow-lg shadow-violet-500/50">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
              </svg>
            </div>
            <div>
              <h3 className="text-2xl font-black text-violet-100">🔊 Audio Response</h3>
              <p className="text-xs text-violet-300 font-bold mt-1">Listen to the advice in {data.audio_language === 'te-IN' ? 'Telugu' : data.audio_language === 'hi-IN' ? 'Hindi' : data.audio_language === 'ta-IN' ? 'Tamil' : data.audio_language || 'native language'}</p>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-2xl p-6 flex items-center gap-4">
            <audio 
              controls 
              className="flex-1 h-12 accent-violet-500"
            >
              <source src={`data:audio/wav;base64,${data.audio_base64}`} type="audio/wav" />
              Your browser does not support the audio element.
            </audio>
            <button
              onClick={() => {
                const audioBlob = new Blob(
                  [Uint8Array.from(atob(data.audio_base64!), c => c.charCodeAt(0))],
                  { type: 'audio/wav' }
                );
                const url = URL.createObjectURL(audioBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `farmer-advice-${data.audio_language || 'audio'}.wav`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
              }}
              className="px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-lg hover:shadow-violet-500/30 transition-all whitespace-nowrap"
              title="Download audio"
            >
              📥 Download
            </button>
          </div>
        </div>
      )}

      {/* Confidence Score Section */}
      <div className="bg-gradient-to-br from-amber-900/40 via-orange-900/40 to-slate-900 rounded-3xl border-2 border-amber-500/30 shadow-lg shadow-amber-500/20 p-8">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start gap-3">
            <div className="p-3 bg-amber-500 rounded-xl shadow-lg shadow-amber-500/30">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-black text-amber-100">Confidence Score</h3>
              <p className="text-xs text-amber-200/70 mt-1 font-medium">How confident we are in this recommendation</p>
            </div>
          </div>
          <span className="text-5xl font-black text-amber-200 drop-shadow-lg">{confidencePercentage}%</span>
        </div>
        
        <div className="mb-6 bg-slate-800/50 rounded-2xl p-5">
          <ConfidenceBar confidence={data.confidence} />
        </div>
        
        <p className={`text-lg font-bold ${
          confidencePercentage >= 80 
            ? "text-emerald-200" 
            : confidencePercentage >= 50 
            ? "text-amber-200"
            : "text-red-200"
        }`}>
          {confidencePercentage >= 80 
            ? "✅ High Confidence - Strongly Recommended"

            : confidencePercentage >= 50 
            ? "⚠ Moderate Confidence - Verify with local experts"
            : "⚠ Low Confidence - Please consult agricultural experts"}
        </p>
      </div>

      {/* Query Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Original Language Card */}
        <div className="bg-white rounded-xl border border-gray-200/60 shadow-sm p-5 hover:shadow-md transition-shadow">
          <h4 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            Your Query Language
          </h4>
          <p className="text-2xl font-bold text-blue-600">{data.original_language || "English"}</p>
          <p className="text-xs text-gray-500 mt-2">Language detected: {data.original_language || "English"}</p>
        </div>

        {/* English Translation Card */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-teal-500/30 shadow-lg p-6 hover:shadow-xl hover:border-teal-500/50 transition-all">
          <h4 className="text-sm font-black text-teal-200 mb-3 flex items-center gap-3">
            <Zap className="w-4 h-4 text-teal-400" />
            Processed Query
          </h4>
          <p className="text-base text-teal-50 leading-relaxed font-semibold">
            {data.translated}
          </p>
        </div>
      </div>

      {/* Alternative Recommendations */}
      {data.all_answers && data.all_answers.length > 0 && (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl border-2 border-slate-700/50 shadow-xl p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-black text-slate-100">✨ Alternative Recommendations</h3>
            <span className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-4 py-2 rounded-full text-sm font-bold shadow-lg shadow-emerald-500/30">
              {Math.min(data.all_answers.length, 10)} options
            </span>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {data.all_answers.slice(0, 10).map((answer, idx) => {
              const isHighConfidence = answer.confidence >= 0.7;
              const isMediumConfidence = answer.confidence >= 0.4;
              
              return (
                <div
                  key={idx}
                  className={`rounded-lg p-4 border-l-4 transition-all hover:shadow-md ${
                    isHighConfidence
                      ? "bg-green-50 border-l-green-500"
                      : isMediumConfidence
                      ? "bg-amber-50 border-l-amber-500"
                      : "bg-red-50 border-l-red-500"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="bg-gray-200 text-gray-700 px-3 py-1 rounded-lg font-bold text-sm">
                        #{answer.rank}
                      </span>
                      <span className={`px-3 py-1 rounded-lg font-bold text-sm ${
                        isHighConfidence
                          ? "bg-green-200 text-green-700"
                          : isMediumConfidence
                          ? "bg-amber-200 text-amber-700"
                          : "bg-red-200 text-red-700"
                      }`}>
                        {Math.round(answer.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-3 overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        isHighConfidence
                          ? "bg-green-500"
                          : isMediumConfidence
                          ? "bg-amber-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${answer.confidence * 100}%` }}
                    />
                  </div>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {answer.text}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Validation Status */}
      {data.is_validated !== undefined && (
        <div className={`rounded-2xl border shadow-md p-6 flex items-start gap-4 ${
          data.is_validated
            ? "bg-green-50 border-green-200/60"
            : "bg-yellow-50 border-yellow-200/60"
        }`}>
          {data.is_validated ? (
            <CheckCircle2 className="w-6 h-6 text-green-600 mt-0.5 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-6 h-6 text-yellow-600 mt-0.5 flex-shrink-0" />
          )}
          <div>
            <p className={`font-bold ${
              data.is_validated ? "text-green-900" : "text-yellow-900"
            }`}>
              {data.is_validated ? "✓ Verified Answer" : "⚠ AI-Generated Answer"}
            </p>
            <p className={`text-sm mt-1 ${
              data.is_validated ? "text-green-800" : "text-yellow-800"
            }`}>
              {data.validation_reason || (data.is_validated 
                ? "This answer has been validated for accuracy and relevance by agricultural experts."
                : "This answer was generated by AI. Please verify with local agricultural experts before implementation.")}
            </p>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-red-50 rounded-2xl border border-red-200/60 shadow-md p-6 flex items-start gap-4">
        <AlertTriangle className="w-6 h-6 text-red-600 mt-0.5 flex-shrink-0" />
        <div>
          <p className="font-bold text-red-900 mb-2">Important Disclaimer</p>
          <p className="text-sm text-red-800 leading-relaxed">
            {data.disclaimer || "⚠️ This answer is provided for informational purposes. Always consult with local agricultural experts, extension officers, or qualified agronomists before making critical farming decisions. Weather, soil, and regional factors may significantly affect results."}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResultsCard;
