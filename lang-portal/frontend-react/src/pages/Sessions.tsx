
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const Sessions = () => {
  const sessions = [
    {
      id: 1,
      activityName: "Typing Tutor",
      groupName: "Core Verbs",
      startTime: "2024-02-08 09:30",
      endTime: "2024-02-08 10:15",
      reviewCount: 25,
    },
    {
      id: 2,
      activityName: "Adventure MUD",
      groupName: "Common Phrases",
      startTime: "2024-02-07 14:20",
      endTime: "2024-02-07 15:05",
      reviewCount: 18,
    },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Study Sessions</h1>
      <div className="grid gap-4">
        {sessions.map((session) => (
          <Card key={session.id}>
            <CardHeader>
              <CardTitle className="text-xl">{session.activityName}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Group</p>
                  <p>{session.groupName}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Start Time</p>
                  <p>{session.startTime}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">End Time</p>
                  <p>{session.endTime}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Reviews</p>
                  <p>{session.reviewCount} items</p>
                </div>
              </div>
              <div className="mt-4">
                <Button variant="outline" size="sm">View Details</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Sessions;
