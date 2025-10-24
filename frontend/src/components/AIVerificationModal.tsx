import { Shield, CheckCircle2, AlertCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

interface AIVerificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  isVerified: boolean;
  reason?: string;
}

export function AIVerificationModal({
  isOpen,
  onClose,
  isVerified,
  reason,
}: AIVerificationModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div
              className={cn(
                "h-12 w-12 rounded-full flex items-center justify-center",
                isVerified ? "bg-success/10" : "bg-destructive/10"
              )}
            >
              <Shield
                className={cn(
                  "h-6 w-6",
                  isVerified ? "text-success" : "text-destructive"
                )}
              />
            </div>
            <div>
              <DialogTitle className="text-xl">AI Verification</DialogTitle>
              <DialogDescription className="flex items-center gap-1 mt-1">
                {isVerified ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-success" />
                    <span>This answer has been verified</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="h-4 w-4 text-destructive" />
                    <span>This answer could not be verified</span>
                  </>
                )}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div className="p-4 rounded-lg bg-muted/50 border">
            <h4 className="font-semibold text-sm mb-2 text-foreground">
              {isVerified ? "Why is this verified?" : "Why wasn't this verified?"}
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {reason ||
                "Our AI system cross-references agricultural best practices, scientific research, and government guidelines to ensure the safety and effectiveness of recommendations."}
            </p>
          </div>

          <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
            <h4 className="font-semibold text-sm mb-2 text-primary flex items-center gap-2">
              <Shield className="h-4 w-4" />
              How AI Verification Works
            </h4>
            <ul className="text-xs text-muted-foreground space-y-1.5">
              <li>• Checks against agricultural databases</li>
              <li>• Validates pesticide dosage and safety</li>
              <li>• Compares with scientific research</li>
              <li>• Ensures crop-specific recommendations</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
