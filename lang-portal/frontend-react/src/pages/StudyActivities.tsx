import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const StudyActivities = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/study_activities`);
        if (!response.ok) throw new Error("Failed to fetch study activities");
        const data = await response.json();
        setActivities(data);
      } catch (error) {
        console.error("Error fetching study activities:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Study Activities</h1>
      {loading ? (
        <p className="text-center text-gray-500">Loading study activities...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Session ID</TableHead>
                <TableHead>Created At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {activities.length > 0 ? (
                activities.map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell>{activity.id}</TableCell>
                    <TableCell>{activity.study_session_id}</TableCell>
                    <TableCell>{new Date(activity.created_at).toLocaleString()}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={3} className="text-center text-gray-500">
                    No study activities found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default StudyActivities;
