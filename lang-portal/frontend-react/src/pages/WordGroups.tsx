import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

const WordGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/groups`);
        if (!response.ok) throw new Error("Failed to fetch word groups");
        const data = await response.json();
        setGroups(data);
      } catch (error) {
        console.error("Error fetching word groups:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchGroups();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Word Groups</h1>
      {loading ? (
        <p className="text-center text-gray-500">Loading word groups...</p>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {groups.length > 0 ? (
                groups.map((group) => (
                  <TableRow key={group.id}>
                    <TableCell>{group.id}</TableCell>
                    <TableCell>{group.name}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={2} className="text-center text-gray-500">
                    No word groups found.
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

export default WordGroups;
