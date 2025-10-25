import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { TrustBadge } from "./TrustBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MessageCircle, Eye, CheckCircle, ThumbsUp } from "lucide-react";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { addCommentToScan, getScanComments, markCommentHelpful } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { Separator } from "@/components/ui/separator";

interface CommunityPostCardProps {
  scanId?: string;
  farmerName: string;
  farmerAvatar?: string;
  farmerLocation?: string;
  trustScore: number;
  title: string;
  description: string;
  imageUrl?: string;
  responseCount: number;
  viewCount: number;
  isResolved: boolean;
  timestamp: string;
  tags: string[];
  confidence?: number;
  onResponseAdded?: () => void; // Callback to refresh the parent
}

export const CommunityPostCard = ({
  scanId,
  farmerName,
  farmerAvatar,
  farmerLocation,
  trustScore,
  title,
  description,
  imageUrl,
  responseCount: initialResponseCount,
  viewCount,
  isResolved,
  timestamp,
  tags,
  confidence,
  onResponseAdded,
}: CommunityPostCardProps) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState("");
  const [isLoadingComments, setIsLoadingComments] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [responseCount, setResponseCount] = useState(initialResponseCount);
  const [markingHelpful, setMarkingHelpful] = useState<{ [key: string]: boolean }>({});

  const handleViewRespond = async () => {
    setIsDialogOpen(true);
    
    if (scanId) {
      try {
        setIsLoadingComments(true);
        const response = await getScanComments(scanId);
        if (response.success) {
          setComments(response.data.comments || []);
          setResponseCount(response.data.comments?.length || 0);
        }
      } catch (error: any) {
        console.error('Error loading comments:', error);
        toast({
          title: "Failed to load responses",
          description: "Could not fetch community responses",
          variant: "destructive",
        });
      } finally {
        setIsLoadingComments(false);
      }
    }
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim() || !scanId) return;

    try {
      setIsSubmitting(true);
      const response = await addCommentToScan(scanId, newComment.trim());
      
      if (response.success) {
        toast({
          title: "Response posted! 🎉",
          description: "Your advice has been shared with the community.",
        });
        setNewComment("");
        
        // Reload comments
        const updatedComments = await getScanComments(scanId);
        if (updatedComments.success) {
          setComments(updatedComments.data.comments || []);
          setResponseCount(updatedComments.data.comments?.length || 0);
        }
        
        // Notify parent to refresh
        if (onResponseAdded) {
          onResponseAdded();
        }
      }
    } catch (error: any) {
      toast({
        title: "Failed to post response",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMarkHelpful = async (commentId: string) => {
    if (!scanId || markingHelpful[commentId]) return;

    try {
      setMarkingHelpful(prev => ({ ...prev, [commentId]: true }));
      const response = await markCommentHelpful(scanId, commentId);
      
      if (response.success) {
        toast({
          title: "Marked as helpful! 👍",
          description: "Thank you for your feedback",
        });
        
        // Update the comment's helpful count locally
        setComments(prev => prev.map(comment => 
          comment.id === commentId 
            ? { ...comment, helpful_count: (comment.helpful_count || 0) + 1 }
            : comment
        ));
      }
    } catch (error: any) {
      toast({
        title: "Failed to mark as helpful",
        description: error.message || "Please try again",
        variant: "destructive",
      });
    } finally {
      setMarkingHelpful(prev => ({ ...prev, [commentId]: false }));
    }
  };
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
          {confidence && (
            <div className="ml-auto">
              <Badge variant="outline" className="text-xs">
                {confidence.toFixed(1)}% Confidence
              </Badge>
            </div>
          )}
        </div>

        <Button 
          variant="outline" 
          className="w-full"
          onClick={handleViewRespond}
        >
          View & Respond
        </Button>
      </CardContent>

      {/* Response Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            <DialogDescription>
              Posted by {farmerName} {farmerLocation && `from ${farmerLocation}`} • {timestamp}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Original Post */}
            <div className="border-b pb-4">
              <p className="text-sm text-muted-foreground mb-3">{description}</p>
              {imageUrl && (
                <img 
                  src={imageUrl.startsWith('http') ? imageUrl : `http://localhost:8000${imageUrl}`}
                  alt={title} 
                  className="w-full rounded-lg border max-h-64 object-cover"
                  onError={(e) => {
                    // Hide image if it fails to load
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              )}
              <div className="flex flex-wrap gap-2 mt-3">
                {tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Comments Section */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-semibold text-sm">
                  Community Responses ({responseCount})
                </h4>
                {responseCount >= 3 && !isResolved && (
                  <Badge variant="outline" className="text-xs text-green-600">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Well Discussed
                  </Badge>
                )}
              </div>
              
              {isLoadingComments ? (
                <div className="text-center py-8">
                  <div className="animate-pulse space-y-3">
                    <div className="h-20 bg-muted rounded-lg"></div>
                    <div className="h-20 bg-muted rounded-lg"></div>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">Loading responses...</p>
                </div>
              ) : comments.length === 0 ? (
                <div className="text-center py-8 border border-dashed rounded-lg">
                  <MessageCircle className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm font-medium text-muted-foreground">No responses yet</p>
                  <p className="text-xs text-muted-foreground mt-1">Be the first to share your advice!</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                  {comments.map((comment: any, index: number) => (
                    <div key={comment.id || index} className="border rounded-lg p-4 space-y-3 hover:shadow-sm transition-shadow">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3 flex-1 min-w-0">
                          <Avatar className="h-10 w-10 flex-shrink-0">
                            <AvatarFallback className="text-xs bg-primary/10 text-primary">
                              {comment.user_name?.charAt(0).toUpperCase() || 'F'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-semibold text-sm truncate">{comment.user_name || 'Anonymous Farmer'}</p>
                              {comment.user_location && (
                                <Badge variant="outline" className="text-xs">
                                  📍 {comment.user_location}
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground">
                              {new Date(comment.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        {comment.helpful_count > 0 && (
                          <Badge className="bg-green-100 text-green-700 hover:bg-green-200 gap-1">
                            <ThumbsUp className="h-3 w-3" />
                            {comment.helpful_count}
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-sm leading-relaxed">{comment.advice}</p>
                      
                      <div className="flex items-center gap-2 pt-2 border-t">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 text-xs gap-1"
                          onClick={() => handleMarkHelpful(comment.id)}
                          disabled={markingHelpful[comment.id]}
                        >
                          <ThumbsUp className="h-3 w-3" />
                          {markingHelpful[comment.id] ? "Marking..." : "Mark as Helpful"}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <Separator />

            {/* Add Response */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <MessageCircle className="h-4 w-4 text-primary" />
                <h4 className="font-semibold text-sm">Share Your Advice</h4>
              </div>
              <Textarea
                placeholder="Share your experience, treatment methods, or helpful advice for this condition..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">
                  {newComment.length}/500 characters
                </p>
                <Button 
                  onClick={handleSubmitComment}
                  disabled={!newComment.trim() || isSubmitting || newComment.length > 500}
                  className="gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Posting...
                    </>
                  ) : (
                    <>
                      <MessageCircle className="h-4 w-4" />
                      Post Response
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
};
