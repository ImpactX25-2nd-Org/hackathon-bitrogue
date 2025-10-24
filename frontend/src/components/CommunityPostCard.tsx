import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { TrustBadge } from "./TrustBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MessageCircle, Eye, CheckCircle } from "lucide-react";

interface CommunityPostCardProps {
  farmerName: string;
  farmerAvatar?: string;
  trustScore: number;
  title: string;
  description: string;
  imageUrl?: string;
  responseCount: number;
  viewCount: number;
  isResolved: boolean;
  timestamp: string;
  tags: string[];
}

export const CommunityPostCard = ({
  farmerName,
  farmerAvatar,
  trustScore,
  title,
  description,
  imageUrl,
  responseCount,
  viewCount,
  isResolved,
  timestamp,
  tags,
}: CommunityPostCardProps) => {
  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3 flex-1">
            <Avatar>
              <AvatarImage src={farmerAvatar} />
              <AvatarFallback className="bg-primary text-primary-foreground">
                {farmerName.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-semibold text-foreground truncate">{farmerName}</h4>
                <TrustBadge score={trustScore} size="sm" />
              </div>
              <p className="text-xs text-muted-foreground">{timestamp}</p>
            </div>
          </div>
          {isResolved && (
            <Badge className="bg-success text-success-foreground gap-1">
              <CheckCircle className="h-3 w-3" />
              Resolved
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <h3 className="font-semibold text-lg text-foreground mb-2">{title}</h3>
          <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
        </div>
        
        {imageUrl && (
          <div className="rounded-lg overflow-hidden border border-border">
            <img src={imageUrl} alt={title} className="w-full h-48 object-cover" />
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <Badge key={index} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="flex items-center gap-4 pt-2">
          <div className="flex items-center gap-2 text-muted-foreground">
            <MessageCircle className="h-4 w-4" />
            <span className="text-sm">{responseCount} responses</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Eye className="h-4 w-4" />
            <span className="text-sm">{viewCount} views</span>
          </div>
        </div>

        <Button variant="outline" className="w-full">View & Respond</Button>
      </CardContent>
    </Card>
  );
};
