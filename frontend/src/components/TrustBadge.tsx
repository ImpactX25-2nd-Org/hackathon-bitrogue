import { Sprout, Wheat, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";

type TrustLevel = "beginner" | "reliable" | "expert";

interface TrustBadgeProps {
  level: TrustLevel;
  score: number;
  className?: string;
  showScore?: boolean;
}

const trustConfig = {
  beginner: {
    icon: Sprout,
    label: "Beginner Farmer",
    color: "text-trust-beginner",
    bgColor: "bg-trust-beginner/10",
    borderColor: "border-trust-beginner/30",
  },
  reliable: {
    icon: Wheat,
    label: "Reliable Farmer",
    color: "text-trust-reliable",
    bgColor: "bg-trust-reliable/10",
    borderColor: "border-trust-reliable/30",
  },
  expert: {
    icon: Trophy,
    label: "Expert Farmer",
    color: "text-trust-expert",
    bgColor: "bg-trust-expert/10",
    borderColor: "border-trust-expert/30",
  },
};

export function TrustBadge({ level, score, className, showScore = true }: TrustBadgeProps) {
  const config = trustConfig[level];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border",
        config.bgColor,
        config.borderColor,
        "transition-all duration-300 hover:scale-105",
        className
      )}
    >
      <Icon className={cn("h-4 w-4", config.color)} />
      <span className={cn("text-sm font-medium", config.color)}>
        {config.label}
      </span>
      {showScore && (
        <span className={cn("text-xs font-semibold ml-1", config.color)}>
          ({score})
        </span>
      )}
    </div>
  );
}
