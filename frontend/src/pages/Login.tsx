import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Sprout, ArrowLeft, Globe, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";
import { Label } from "@/components/ui/label";
import { useLanguage, languages } from "@/contexts/LanguageContext";
import { loginUser as loginUserAPI } from "@/lib/api";

export default function Login() {
  const navigate = useNavigate();
  const { currentLanguage, setLanguage } = useLanguage();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!identifier || !password) {
      toast({
        title: "Missing information",
        description: "Please enter both phone/email and password",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Call actual backend API
      const result = await loginUserAPI({
        identifier,
        password,
        language: currentLanguage,
      });

      if (result.success && result.token && result.user) {
        // Store auth token and user data
        localStorage.setItem("authToken", result.token);
        localStorage.setItem("userData", JSON.stringify(result.user));

        toast({
          title: "Login successful!",
          description: `Welcome back, ${result.user.name}`,
        });

        // Navigate to dashboard
        navigate("/dashboard");
      } else {
        toast({
          title: "Login failed",
          description: result.message || "Invalid credentials",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      toast({
        title: "Login failed",
        description: error.message || "Invalid credentials. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToHome = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-green-50/50">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleBackToHome}
                className="mr-2"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <Sprout className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-3xl font-bold text-foreground">KrishiLok</h1>
                <p className="text-sm text-muted-foreground">Sign in to continue</p>
              </div>
            </div>
            
            {/* Language Selector */}
            <div className="flex items-center gap-3">
              <Select value={currentLanguage} onValueChange={setLanguage}>
                <SelectTrigger className="w-[160px]">
                  <Globe className="h-4 w-4 mr-2 text-primary" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      <span className="font-medium">{lang.nativeName}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-md mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Login Card */}
          <Card className="border-2">
            <CardHeader className="space-y-1">
              <div className="flex justify-center mb-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <Sprout className="h-10 w-10 text-primary" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold text-center text-foreground">
                Welcome Back
              </CardTitle>
              <CardDescription className="text-center">
                Sign in to access your farming community
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} className="space-y-4">
                {/* Phone/Email Input */}
                <div className="space-y-2">
                  <Label htmlFor="identifier" className="text-sm font-medium">
                    Phone Number or Email
                  </Label>
                  <Input
                    id="identifier"
                    type="text"
                    placeholder="Enter your phone or email"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    className="h-11"
                    disabled={isLoading}
                  />
                </div>

                {/* Password Input */}
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11"
                    disabled={isLoading}
                  />
                </div>

                {/* Forgot Password Link */}
                <div className="flex justify-end">
                  <Button
                    type="button"
                    variant="link"
                    className="px-0 text-primary hover:text-primary/80 text-sm"
                    onClick={() => {
                      toast({
                        title: "Feature coming soon",
                        description: "Password recovery will be available after backend integration",
                      });
                    }}
                  >
                    Forgot password?
                  </Button>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full h-11 font-semibold"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    "Sign In"
                  )}
                </Button>

                {/* Divider */}
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">Or</span>
                  </div>
                </div>

                {/* Sign Up Link */}
                <div className="text-center">
                  <span className="text-sm text-muted-foreground">
                    Don't have an account?{" "}
                  </span>
                  <Button
                    type="button"
                    variant="link"
                    className="px-1 text-primary hover:text-primary/80 font-semibold text-sm"
                    onClick={() => navigate("/signup")}
                    disabled={isLoading}
                  >
                    Sign up
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Info Note */}
          <div className="mt-6 text-center">
            <p className="text-xs text-muted-foreground bg-muted rounded-lg p-3">
              � Secure login with backend authentication
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
