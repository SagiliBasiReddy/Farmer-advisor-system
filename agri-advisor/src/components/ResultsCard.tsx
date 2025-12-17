import { Languages, HelpCircle, Lightbulb, AlertTriangle, Gauge } from "lucide-react";
import ConfidenceBar from "./ConfidenceBar";

interface AdvisoryResponse {
  translated: string;
  canonical: string;
  advice: string;
  confidence: number;
  disclaimer: string;
}

interface ResultsCardProps {
  data: AdvisoryResponse;
}

const ResultsCard = ({ data }: ResultsCardProps) => {
  return (
    <div className="w-full max-w-2xl mx-auto px-4 space-y-4">
      {/* Translated Text Card */}
      <div className="card-agricultural p-5 animate-fade-up opacity-0 stagger-1">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-secondary rounded-xl shrink-0">
            <Languages className="w-5 h-5 text-secondary-foreground" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-muted-foreground mb-1">
              Translated Text
            </h3>
            <p className="text-foreground leading-relaxed">
              {data.translated}
            </p>
          </div>
        </div>
      </div>

      {/* Canonical Question Card */}
      <div className="card-agricultural p-5 animate-fade-up opacity-0 stagger-2">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-muted rounded-xl shrink-0">
            <HelpCircle className="w-5 h-5 text-muted-foreground" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-muted-foreground mb-1">
              Canonical Question
            </h3>
            <p className="text-foreground leading-relaxed">
              {data.canonical}
            </p>
          </div>
        </div>
      </div>

      {/* Recommended Action Card - Highlighted */}
      <div className="card-agricultural p-5 border-2 border-primary/30 bg-primary/5 animate-fade-up opacity-0 stagger-3">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-primary rounded-xl shrink-0">
            <Lightbulb className="w-5 h-5 text-primary-foreground" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-primary mb-2">
              Recommended Action
            </h3>
            <p className="text-foreground leading-relaxed text-lg">
              {data.advice}
            </p>
          </div>
        </div>
      </div>

      {/* Confidence Score Card */}
      <div className="card-agricultural p-5 animate-fade-up opacity-0 stagger-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-accent/20 rounded-xl shrink-0">
            <Gauge className="w-5 h-5 text-accent-foreground" />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-muted-foreground mb-3">
              Confidence Score
            </h3>
            <ConfidenceBar confidence={data.confidence} />
          </div>
        </div>
      </div>

      {/* Disclaimer Card */}
      <div className="card-agricultural p-4 bg-secondary/50 border-secondary animate-fade-up opacity-0 stagger-5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-accent shrink-0 mt-0.5" />
          <p className="text-sm text-muted-foreground leading-relaxed">
            {data.disclaimer}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResultsCard;
