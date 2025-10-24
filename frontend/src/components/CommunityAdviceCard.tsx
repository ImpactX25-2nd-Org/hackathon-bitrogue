import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { TrustBadge } from "./TrustBadge";
import { ThumbsUp, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CommunityAdviceCardProps {
  farmerName: string;
  farmerAvatar?: string;
  trustScore: number;
  advice: string;
  helpfulCount: number;
  responseCount: number;
  timestamp: string;
}

export const CommunityAdviceCard = ({
  farmerName,
  farmerAvatar,
  trustScore,
  advice,
  helpfulCount,
  responseCount,
  timestamp,
}: CommunityAdviceCardProps) => {
  return (
    <Card className="border-l-4 border-l-primary hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center gap-4 pb-3">
        <Avatar>
          <AvatarImage src={farmerAvatar} />
          <AvatarFallback className="bg-primary text-primary-foreground">
            {farmerName.charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-foreground">{farmerName}</h4>
            <TrustBadge score={trustScore} size="sm" />
          </div>
          <p className="text-xs text-muted-foreground">{timestamp}</p>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-foreground leading-relaxed">{advice}</p>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" className="gap-2">
            <ThumbsUp className="h-4 w-4" />
            <span className="text-xs">{helpfulCount} Helpful</span>
          </Button>
          <Button variant="ghost" size="sm" className="gap-2">
            <MessageCircle className="h-4 w-4" />
            <span className="text-xs">{responseCount} Responses</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
