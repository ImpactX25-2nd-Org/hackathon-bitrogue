import { useState } from "react";
import { User, ThumbsUp, Shield, Info } from "lucide-react";
import { TrustBadge } from "./TrustBadge";
import { Button } from "@/components/ui/button";
import { AIVerificationModal } from "./AIVerificationModal";
import { cn } from "@/lib/utils";

interface AnswerCardProps {
  id: string;
  author: string;
  authorLevel: "beginner" | "reliable" | "expert";
  authorScore: number;
  content: string;
  isVerified: boolean;
  verificationReason?: string;
  helpful: number;
  timestamp: string;
}

export function AnswerCard({
  author,
  authorLevel,
  authorScore,
  content,
  isVerified,
  verificationReason,
  helpful,
  timestamp,
}: AnswerCardProps) {
  const [showVerification, setShowVerification] = useState(false);
  const [helpfulCount, setHelpfulCount] = useState(helpful);
  const [hasVoted, setHasVoted] = useState(false);

  const handleHelpful = () => {
    if (!hasVoted) {
      setHelpfulCount(helpfulCount + 1);
      setHasVoted(true);
    }
  };

  return (
    <>
      <div className="p-4 rounded-lg bg-muted/30 border border-border space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="font-medium text-sm text-foreground">{author}</p>
              <TrustBadge level={authorLevel} score={authorScore} showScore={false} className="mt-1" />
            </div>
          </div>
          <span className="text-xs text-muted-foreground">{timestamp}</span>
        </div>

        <p className="text-sm text-foreground leading-relaxed">{content}</p>

        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-3">
            {isVerified && (
              <button
                onClick={() => setShowVerification(true)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-full",
                  "bg-success/10 border border-success/30",
                  "text-success text-xs font-medium",
                  "hover:bg-success/20 transition-colors cursor-pointer"
                )}
              >
                <Shield className="h-3.5 w-3.5" />
                <span>✓ Verified by AI</span>
                <Info className="h-3 w-3 opacity-70" />
              </button>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleHelpful}
            disabled={hasVoted}
            className={cn("gap-2", hasVoted && "text-primary")}
          >
            <ThumbsUp className={cn("h-4 w-4", hasVoted && "fill-primary")} />
            <span className="font-medium">{helpfulCount}</span>
          </Button>
        </div>
      </div>

      <AIVerificationModal
        isOpen={showVerification}
        onClose={() => setShowVerification(false)}
        isVerified={isVerified}
        reason={verificationReason}
      />
    </>
  );
}
