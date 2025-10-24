import { CommunityPostCard } from "./CommunityPostCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Search } from "lucide-react";
import { useState } from "react";
import { openNewPostWithPrefill } from "@/lib/api-placeholders";
import type { CommunityPrefill } from "@/lib/api-placeholders";

interface CommunityDashboardProps {
  prefillData?: CommunityPrefill;
}

const mockPosts = [
  {
    farmerName: "Rajesh Kumar",
    trustScore: 85,
    title: "Yellowing leaves on tomato plants",
    description: "My tomato plants are showing yellow leaves with brown spots. Started 3 days ago. Need urgent help!",
    responseCount: 12,
    viewCount: 234,
    isResolved: false,
    timestamp: "2 hours ago",
    tags: ["Tomato", "Disease", "Urgent"],
    imageUrl: "https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400&h=300&fit=crop",
  },
  {
    farmerName: "Priya Sharma",
    trustScore: 92,
    title: "Successful treatment of wheat rust",
    description: "Sharing my experience treating yellow rust in wheat. Applied fungicide and results are excellent.",
    responseCount: 28,
    viewCount: 567,
    isResolved: true,
    timestamp: "5 hours ago",
    tags: ["Wheat", "Rust", "Success Story"],
    imageUrl: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=300&fit=crop",
  },
  {
    farmerName: "Amit Patil",
    trustScore: 78,
    title: "Cotton boll worm infestation",
    description: "Need advice on organic methods to control boll worm. Chemical pesticides not working effectively.",
    responseCount: 15,
    viewCount: 189,
    isResolved: false,
    timestamp: "1 day ago",
    tags: ["Cotton", "Pest", "Organic"],
  },
];

export const CommunityDashboard = ({ prefillData }: CommunityDashboardProps = {}) => {
  const [newPostPrefill, setNewPostPrefill] = useState(prefillData);

  const handleNewPost = () => {
    // Call placeholder function to open new post modal with prefill
    openNewPostWithPrefill(newPostPrefill || {});
    
    // In production, this will:
    // 1. Open a modal/drawer with a post creation form
    // 2. Prefill the form with image, cropName, description if provided
    // 3. Allow user to edit and submit
    console.log("Opening new post with prefill:", newPostPrefill);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Community Dashboard</h2>
          <p className="text-muted-foreground">Connect with fellow farmers and share knowledge</p>
        </div>
        <Button 
          className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90"
          onClick={handleNewPost}
        >
          <Plus className="h-4 w-4" />
          New Post
        </Button>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search posts, crops, or diseases..."
            className="pl-10"
          />
        </div>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-3 max-w-md">
          <TabsTrigger value="all">All Posts</TabsTrigger>
          <TabsTrigger value="unresolved">Unresolved</TabsTrigger>
          <TabsTrigger value="resolved">Resolved</TabsTrigger>
        </TabsList>
        <TabsContent value="all" className="mt-6 space-y-4">
          {mockPosts.map((post, index) => (
            <CommunityPostCard key={index} {...post} />
          ))}
        </TabsContent>
        <TabsContent value="unresolved" className="mt-6 space-y-4">
          {mockPosts.filter(p => !p.isResolved).map((post, index) => (
            <CommunityPostCard key={index} {...post} />
          ))}
        </TabsContent>
        <TabsContent value="resolved" className="mt-6 space-y-4">
          {mockPosts.filter(p => p.isResolved).map((post, index) => (
            <CommunityPostCard key={index} {...post} />
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
};
