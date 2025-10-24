import { useState } from "react";
import { MessageCircle, ThumbsUp, Clock, User } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrustBadge } from "./TrustBadge";
import { AnswerCard } from "./AnswerCard";
import { cn } from "@/lib/utils";

interface Answer {
  id: string;
  author: string;
  authorLevel: "beginner" | "reliable" | "expert";
  authorScore: number;
  content: string;
  isVerified: boolean;
  verificationReason?: string;
  helpful: number;
  timestamp: string;
}

interface QuestionCardProps {
  id: string;
  author: string;
  authorLevel: "beginner" | "reliable" | "expert";
  authorScore: number;
  question: string;
  description?: string;
  answers: Answer[];
  timestamp: string;
  tags?: string[];
}

export function QuestionCard({
  author,
  authorLevel,
  authorScore,
  question,
  description,
  answers,
  timestamp,
  tags,
}: QuestionCardProps) {
  const [showAnswers, setShowAnswers] = useState(false);
  const verifiedAnswers = answers.filter((a) => a.isVerified).length;

  return (
    <Card className="hover:shadow-lg transition-all duration-300">
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-semibold text-foreground">{author}</p>
              <div className="flex items-center gap-2 mt-1">
                <TrustBadge level={authorLevel} score={authorScore} showScore={false} />
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {timestamp}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">{question}</h3>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 text-xs rounded-md bg-primary/10 text-primary font-medium"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </CardHeader>
      <CardFooter className="flex items-center justify-between pt-4 border-t">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowAnswers(!showAnswers)}
          className="gap-2"
        >
          <MessageCircle className="h-4 w-4" />
          <span>{answers.length} Answers</span>
          {verifiedAnswers > 0 && (
            <span className="text-success font-semibold">({verifiedAnswers} ✓)</span>
          )}
        </Button>
        <Button variant="ghost" size="sm" className="gap-2">
          <ThumbsUp className="h-4 w-4" />
          <span>Helpful</span>
        </Button>
      </CardFooter>
      {showAnswers && (
        <CardContent className={cn("space-y-4 pt-4 border-t animate-in fade-in-50 slide-in-from-top-2")}>
          {answers.map((answer) => (
            <AnswerCard key={answer.id} {...answer} />
          ))}
        </CardContent>
      )}
    </Card>
  );
}
