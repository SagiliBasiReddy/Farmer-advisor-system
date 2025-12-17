import { Wheat } from "lucide-react";

const Header = () => {
  return (
    <header className="w-full py-8 px-4 text-center">
      {/* Logo and Title */}
      <div className="flex items-center justify-center gap-3 mb-3">
        <div className="p-3 bg-primary/10 rounded-2xl">
          <Wheat className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground">
          Farmer Advisory System
        </h1>
      </div>

      {/* Subtitle */}
      <p className="text-lg text-muted-foreground max-w-md mx-auto">
        Multilingual AI-assisted crop advisory
      </p>

      {/* Decorative Element */}
      <div className="mt-6 flex items-center justify-center gap-2">
        <div className="h-px w-12 bg-border" />
        <div className="w-2 h-2 rounded-full bg-primary/40" />
        <div className="h-px w-12 bg-border" />
      </div>
    </header>
  );
};

export default Header;
