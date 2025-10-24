import { User, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrustBadge } from "./TrustBadge";

interface TopFarmer {
  id: string;
  name: string;
  level: "beginner" | "reliable" | "expert";
  score: number;
  helpfulAnswers: number;
}

const topFarmers: TopFarmer[] = [
  { id: "1", name: "Rajesh Kumar", level: "expert", score: 1250, helpfulAnswers: 89 },
  { id: "2", name: "Priya Singh", level: "expert", score: 1180, helpfulAnswers: 76 },
  { id: "3", name: "Amit Patel", level: "reliable", score: 890, helpfulAnswers: 54 },
  { id: "4", name: "Sunita Devi", level: "reliable", score: 720, helpfulAnswers: 43 },
];

export function TopFarmersCard() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5 text-primary" />
          Top Trusted Farmers
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {topFarmers.map((farmer, index) => (
          <div
            key={farmer.id}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
              {index + 1}
            </div>
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm text-foreground truncate">{farmer.name}</p>
              <TrustBadge level={farmer.level} score={farmer.score} showScore={false} className="mt-1" />
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Helpful</p>
              <p className="text-sm font-semibold text-primary">{farmer.helpfulAnswers}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
