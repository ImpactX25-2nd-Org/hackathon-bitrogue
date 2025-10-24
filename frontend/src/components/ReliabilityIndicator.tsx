import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertCircle, XCircle } from "lucide-react";

interface ReliabilityIndicatorProps {
  percentage: number;
}

export const ReliabilityIndicator = ({ percentage }: ReliabilityIndicatorProps) => {
  const getReliabilityData = () => {
    if (percentage >= 90) {
      return {
        variant: "success" as const,
        icon: CheckCircle2,
        label: "High Reliability",
        color: "text-success",
      };
    }
    if (percentage >= 60) {
      return {
        variant: "warning" as const,
        icon: AlertCircle,
        label: "Medium Reliability",
        color: "text-warning",
      };
    }
    return {
      variant: "destructive" as const,
      icon: XCircle,
      label: "Low Reliability",
      color: "text-destructive",
    };
  };

  const data = getReliabilityData();
  const Icon = data.icon;

  return (
    <Badge variant={data.variant} className="gap-2 px-4 py-2 text-sm font-semibold">
      <Icon className="h-4 w-4" />
      <span>{data.label} ({percentage}%)</span>
    </Badge>
  );
};
