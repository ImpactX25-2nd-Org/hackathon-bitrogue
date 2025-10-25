import { CommunityPostCard } from "./CommunityPostCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Search } from "lucide-react";
import { useState, useEffect } from "react";
import { getCommunityScans } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { useLanguage } from "@/contexts/LanguageContext";

interface CommunityDashboardProps {
  prefillData?: any;
}

export const CommunityDashboard = ({ prefillData }: CommunityDashboardProps = {}) => {
  const [posts, setPosts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const { currentLanguage } = useLanguage();

  // Load community scans on mount
  const loadCommunityScans = async () => {
    try {
      setIsLoading(true);
      console.log(`🌐 Loading community scans with language: ${currentLanguage}`);
      const response = await getCommunityScans(0, 20, undefined, undefined, currentLanguage);
      console.log(`✓ Community scans response:`, response);
      
      if (response.success && response.data.scans) {
        // Transform backend scans to match CommunityPostCard format
        const transformedPosts = response.data.scans.map((scan: any) => {
          // Handle image URL - prepend backend URL if needed
          let imageUrl = scan.image_url;
          if (imageUrl && imageUrl.startsWith('/uploads')) {
            imageUrl = `http://localhost:8000${imageUrl}`;
          }
          
          return {
            scanId: scan.id,
            farmerName: scan.user_name || "Anonymous Farmer",
            farmerLocation: scan.user_location || "Unknown",
            trustScore: Math.min(95, Math.max(60, scan.reliability || 75)), // Use reliability as base trust score
            title: `${scan.crop_name} - ${scan.disease_name?.replace(/_/g, ' ') || 'Disease Detection'}`,
            description: scan.description || `Disease detected: ${scan.disease_name}`,
            responseCount: scan.comments_count || 0,
            viewCount: Math.floor(Math.random() * 300) + 50, // Mock for now
            isResolved: scan.comments_count >= 3, // Consider resolved if has 3+ responses
            timestamp: new Date(scan.created_at).toLocaleString(),
            tags: [
              scan.crop_name,
              scan.disease_name?.includes('healthy') ? 'Healthy' : 'Disease',
              scan.reliability > 80 ? 'High Confidence' : 'Needs Review'
            ],
            imageUrl: imageUrl,
            confidence: scan.reliability,
          };
        });
        
        setPosts(transformedPosts);
        console.log('✅ Loaded community scans:', transformedPosts.length);
      }
    } catch (error: any) {
      console.error('❌ Error loading community scans:', error);
      toast({
        title: "Failed to load community posts",
        description: error.message || "Please try again later",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCommunityScans();
  }, [currentLanguage]); // Reload when language changes

  const handleNewPost = () => {
    toast({
      title: "Feature Coming Soon",
      description: "New post creation will be available soon!",
    });
  };

  const handleResponseAdded = () => {
    // Refresh the community feed when a response is added
    console.log('🔄 Refreshing community feed after response...');
    loadCommunityScans();
  };

  const filteredPosts = posts.filter(post => 
    searchQuery === "" || 
    post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    post.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    post.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

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
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading community posts...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No community posts yet. Be the first to share!</p>
        </div>
      ) : (
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="all">All Posts ({filteredPosts.length})</TabsTrigger>
            <TabsTrigger value="unresolved">Unresolved ({filteredPosts.filter(p => !p.isResolved).length})</TabsTrigger>
            <TabsTrigger value="resolved">Resolved ({filteredPosts.filter(p => p.isResolved).length})</TabsTrigger>
          </TabsList>
          <TabsContent value="all" className="mt-6 space-y-4">
            {filteredPosts.map((post, index) => (
              <CommunityPostCard 
                key={post.scanId || index} 
                {...post} 
                onResponseAdded={handleResponseAdded}
              />
            ))}
          </TabsContent>
          <TabsContent value="unresolved" className="mt-6 space-y-4">
            {filteredPosts.filter(p => !p.isResolved).map((post, index) => (
              <CommunityPostCard 
                key={post.scanId || index} 
                {...post}
                onResponseAdded={handleResponseAdded}
              />
            ))}
          </TabsContent>
          <TabsContent value="resolved" className="mt-6 space-y-4">
            {filteredPosts.filter(p => p.isResolved).map((post, index) => (
              <CommunityPostCard 
                key={post.scanId || index} 
                {...post}
                onResponseAdded={handleResponseAdded}
              />
            ))}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};
