import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ReliabilityIndicator } from "./ReliabilityIndicator";
import { CommunityAdviceCard } from "./CommunityAdviceCard";
import { Button } from "@/components/ui/button";
import { Share2, AlertTriangle, Volume2 } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { playTranslatedMessage, shareToCommunity } from "@/lib/api-placeholders";
import { toast } from "@/hooks/use-toast";
import { useState } from "react";

interface DiseaseDetectionResultProps {
  diseaseName: string;
  reliability: number;
  nextSteps: string[];
  communityAdvice?: Array<{
    farmerName: string;
    farmerLocation?: string;
    advice: string;
    helpfulCount: number;
    timestamp: string;
  }>;
  isCommon: boolean;
}

export const DiseaseDetectionResult = ({
  diseaseName,
  reliability,
  nextSteps,
  communityAdvice,
  isCommon,
}: DiseaseDetectionResultProps) => {
  const [isSharing, setIsSharing] = useState(false);

  const handlePlayMessage = async () => {
    try {
      const result = await playTranslatedMessage("mock_scan_id");
      toast({
        title: "Playing message",
        description: "Audio will be available after backend integration",
      });
      console.log("Audio URL:", result.audioUrl);
    } catch (error) {
      toast({
        title: "Audio not available",
        description: "Backend integration required",
        variant: "destructive",
      });
    }
  };

  const handleShareToCommunity = async () => {
    setIsSharing(true);
    try {
      // Call placeholder function with prefill data
      // In production, this will come from the scan context
      await shareToCommunity({
        cropName: "Mock Crop", // Will come from scan data
        description: diseaseName,
        image: "/placeholder.svg", // Will come from scan data
      });

      toast({
        title: "Shared to community",
        description: "Your post has been created in the community dashboard",
      });

      // Navigate to community dashboard (will be implemented with router)
      console.log("Navigate to community dashboard with new post");
    } catch (error) {
      toast({
        title: "Share failed",
        description: "Could not share to community. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSharing(false);
    }
  };

  // Format disease name for better display
  const formatDiseaseName = (name: string) => {
    // Convert snake_case to Title Case
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="space-y-6">
      <Card className="border-2 border-primary">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl text-foreground">{formatDiseaseName(diseaseName)}</CardTitle>
              <ReliabilityIndicator percentage={reliability} />
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              className="gap-2"
              onClick={handleShareToCommunity}
              disabled={isSharing}
            >
              <Share2 className="h-4 w-4" />
              Share to Community
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold text-foreground mb-3">Suggested Next Steps:</h3>
            <ul className="space-y-2">
              {nextSteps.map((step, index) => (
                <li key={index} className="flex gap-3 text-sm">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">
                    {index + 1}
                  </span>
                  <span className="text-foreground">{step}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Play Message Button */}
          <Button 
            variant="secondary" 
            className="w-full gap-2 mt-4"
            onClick={handlePlayMessage}
          >
            <Volume2 className="h-4 w-4" />
            Play message (your language)
          </Button>
        </CardContent>
      </Card>

      {/* Community Advice - Always show below ML result */}
      {isCommon && communityAdvice && communityAdvice.length > 0 && (
        <div 
          className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-250"
        >
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-semibold text-foreground">
              💡 Community Solutions
            </h3>
            <span className="text-sm text-muted-foreground">
              ({communityAdvice.length} {communityAdvice.length === 1 ? 'farmer' : 'farmers'} shared proven solutions)
            </span>
            {/* Show warning badge if low confidence */}
            {reliability <= 25 && (
              <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-medium">
                Low Confidence - Community Input Recommended
              </span>
            )}
          </div>
          <div className="space-y-4">
            {communityAdvice.map((advice, index) => (
              <CommunityAdviceCard 
                key={index} 
                farmerName={advice.farmerName}
                farmerLocation={advice.farmerLocation}
                trustScore={Math.min(95, 60 + (advice.helpfulCount * 5))} // Calculate trust score from helpful count
                advice={advice.advice}
                helpfulCount={advice.helpfulCount}
                responseCount={0} // Not available yet
                timestamp={new Date(advice.timestamp).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              />
            ))}
          </div>
        </div>
      )}

      {!isCommon && (
        <Card className="bg-warning/10 border-warning">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <AlertTriangle className="h-6 w-6 text-warning flex-shrink-0 mt-1" />
              <div className="space-y-2">
                <h3 className="font-semibold text-foreground">Rare Disease Detected</h3>
                <p className="text-sm text-muted-foreground">
                  This disease is uncommon in our community records. We recommend posting this to the
                  community dashboard to get input from experienced farmers and extension workers.
                </p>
                <Button className="mt-3 bg-warning text-warning-foreground hover:bg-warning/90">
                  Post to Community Dashboard
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
