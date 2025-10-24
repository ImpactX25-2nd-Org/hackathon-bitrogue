import { Badge } from "@/components/ui/badge";
import { Shield } from "lucide-react";

interface TrustBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
}

export const TrustBadge = ({ score, size = "md" }: TrustBadgeProps) => {
  const getVariant = () => {
    if (score >= 80) return "success";
    if (score >= 50) return "warning";
    return "destructive";
  };

  const getColor = () => {
    if (score >= 80) return "text-success";
    if (score >= 50) return "text-warning";
    return "text-destructive";
  };

  const sizeClass = size === "sm" ? "text-xs" : size === "lg" ? "text-base" : "text-sm";

  return (
    <Badge variant={getVariant()} className={`${sizeClass} gap-1 font-semibold`}>
      <Shield className="h-3 w-3" />
      <span>Trust: {score}%</span>
    </Badge>
  );
};
