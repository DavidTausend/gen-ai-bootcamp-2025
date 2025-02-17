import { useState, useEffect } from "react";
import { ArrowRight, Book, CheckCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { API_BASE_URL } from "../config";

const Dashboard = () => {
  const [studySession, setStudySession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLastStudySession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/last_study_session`);
        if (!response.ok) throw new Error("Failed to fetch");
        const data = await response.json();
        setStudySession(data);
      } catch (error) {
        console.error("Error fetching last study session:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLastStudySession();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in slide-up">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <Button className="bg-primary hover:bg-primary/90">
          Start Studying <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl">80%</CardTitle>
            <p className="text-sm text-muted-foreground">Success Rate</p>
          </CardHeader>
          <CardContent>
            <Progress value={80} className="h-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl">124</CardTitle>
            <p className="text-sm text-muted-foreground">Total Words</p>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-green-500">
              <CheckCircle className="w-4 h-4 mr-2" />
              <span className="text-sm">3 mastered today</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl">1 day</CardTitle>
            <p className="text-sm text-muted-foreground">Study Streak</p>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-blue-500">
              <Clock className="w-4 h-4 mr-2" />
              <span className="text-sm">Keep it up!</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Last Study Session</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-gray-500">Loading...</p>
          ) : studySession ? (
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">{studySession.activity_name || "Typing Tutor"}</h3>
                <p className="text-sm text-muted-foreground">{studySession.created_at || "N/A"}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div>
                  <span className="text-green-500 font-medium">{studySession.correct || 0} correct</span>
                  <span className="mx-2">•</span>
                  <span className="text-red-500 font-medium">{studySession.wrong || 0} wrong</span>
                </div>
                <Button variant="outline" size="sm">
                  View Details
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No recent sessions found.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
