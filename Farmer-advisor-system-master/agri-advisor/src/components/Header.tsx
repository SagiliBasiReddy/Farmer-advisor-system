import { Leaf, Sparkles } from "lucide-react";

const Header = () => {
  return (
    <header className="w-full relative overflow-hidden">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-green-900 to-slate-900" />
      <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-500/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }} />
      
      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-16">
        {/* Logo and Title */}
        <div className="flex flex-col items-center gap-6 mb-4">
          <div className="flex items-center gap-4 group">
            <div className="p-4 bg-gradient-to-br from-emerald-400 via-green-500 to-teal-600 rounded-2xl shadow-2xl shadow-emerald-500/50 group-hover:shadow-emerald-500/80 transition-all duration-300 group-hover:scale-110">
              <Leaf className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-black bg-gradient-to-r from-emerald-200 via-green-200 to-teal-200 bg-clip-text text-transparent drop-shadow-lg">
                SRM Agro Advisor
              </h1>
              <p className="text-sm sm:text-base text-emerald-300 font-bold ml-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                AI-Powered Agricultural Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Subtitle */}
        <p className="text-center text-emerald-50/80 text-sm sm:text-lg mt-6 max-w-3xl mx-auto font-medium">
          🌾 Crop Care • 🐛 Pest Management • 🌱 Fertilization • 💧 Irrigation • 🌍 Any Language
        </p>

        {/* Decorative animated line */}
        <div className="mt-8 flex items-center justify-center gap-4">
          <div className="h-px flex-1 max-w-xs bg-gradient-to-r from-transparent via-emerald-400 to-transparent" />
          <div className="flex gap-2">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="w-3 h-3 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 shadow-lg shadow-emerald-500/50"
                style={{
                  animation: `bounce ${0.8 + i * 0.1}s infinite`,
                }}
              />
            ))}
          </div>
          <div className="h-px flex-1 max-w-xs bg-gradient-to-r from-transparent via-teal-400 to-transparent" />
        </div>
      </div>
    </header>
  );
};

export default Header;
