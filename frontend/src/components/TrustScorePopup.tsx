import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Star } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { submitTrustScore } from "@/lib/api-placeholders";

interface TrustScorePopupProps {
  open: boolean;
  onClose: () => void;
  suggestionId: string;
  farmerName: string;
}

export const TrustScorePopup = ({
  open,
  onClose,
  suggestionId,
  farmerName,
}: TrustScorePopupProps) => {
  const [score, setScore] = useState<number>(3);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Call placeholder function for backend integration
      await submitTrustScore(suggestionId, score);
      
      toast({
        title: "Feedback submitted",
        description: `Thank you for rating ${farmerName}'s advice!`,
      });
      
      // Update trust score locally (frontend demo)
      console.log(`Trust score updated: ${score}/5 for suggestion ${suggestionId}`);
      
      onClose();
    } catch (error) {
      toast({
        title: "Feedback recorded",
        description: "Backend integration pending",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNotYet = () => {
    toast({
      title: "Reminder set",
      description: "We'll ask again in a few days",
    });
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-foreground">How did it work?</DialogTitle>
          <DialogDescription>
            Did {farmerName}'s suggestion help solve your crop issue?
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Star Rating Visual */}
          <div className="flex justify-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onClick={() => setScore(star)}
                className="focus:outline-none transition-transform hover:scale-110"
              >
                <Star
                  className={`h-8 w-8 ${
                    star <= score
                      ? "fill-warning text-warning"
                      : "text-muted-foreground"
                  }`}
                />
              </button>
            ))}
          </div>

          {/* Score Labels */}
          <div className="text-center">
            <p className="text-2xl font-bold text-foreground">{score} / 5</p>
            <p className="text-sm text-muted-foreground mt-1">
              {score === 1 && "Not helpful"}
              {score === 2 && "Slightly helpful"}
              {score === 3 && "Moderately helpful"}
              {score === 4 && "Very helpful"}
              {score === 5 && "Extremely helpful"}
            </p>
          </div>

          {/* Slider Alternative */}
          <div className="space-y-2">
            <label className="text-sm text-muted-foreground">Adjust your rating:</label>
            <Slider
              value={[score]}
              onValueChange={(value) => setScore(value[0])}
              min={1}
              max={5}
              step={1}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleNotYet}
              className="flex-1"
            >
              Not Yet
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex-1"
            >
              Submit
            </Button>
          </div>

          {/* Backend Integration Note */}
          <p className="text-xs text-muted-foreground text-center">
            This popup should trigger ~10-15 days after marking "Tried this" (backend scheduling required)
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};
