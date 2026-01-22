import { useEffect, useState } from "react";
import { Calendar, MapPin, ChevronDown, CheckCircle, XCircle, Filter, Loader2, AlertCircle } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { api, PastDisaster } from "@/lib/api";

export default function PastDisasters() {
  const [disasters, setDisasters] = useState<PastDisaster[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDisasters = async () => {
      try {
        // Query for generic disaster context to get a broad list initially
        // or effectively "list all" if we had that endpoint. 
        // Using a generic query for now to populate the view.
        const response = await api.post<PastDisaster[]>("/memory/retrieve", {
          query_text: "major earthquake with structural damage and social impact",
          top_k: 6
        });
        setDisasters(response.data);
      } catch (error) {
        console.error("Failed to fetch past disasters:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDisasters();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="page-header mb-6 -mx-6 -mt-6 px-6 py-4">
        <h1 className="page-title">Similar Past Disasters</h1>
        <p className="page-subtitle">
          Comparison with historically similar earthquake events
        </p>
      </div>

      {/* Filter Controls */}
      <div className="content-card mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium text-foreground">Filter Historical Events</span>
        </div>
        <div className="grid gap-6 sm:grid-cols-3">
          {/* Magnitude Range */}
          <div className="space-y-3">
            <Label className="text-sm text-muted-foreground">Magnitude Range</Label>
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground">5.0</span>
              <Slider defaultValue={[5.5, 8.0]} min={5} max={9} step={0.1} className="flex-1" />
              <span className="text-xs text-muted-foreground">9.0</span>
            </div>
            <p className="text-xs text-muted-foreground text-center">5.5 – 8.0</p>
          </div>

          {/* Region */}
          <div className="space-y-3">
            <Label className="text-sm text-muted-foreground">Region</Label>
            <Select defaultValue="all">
              <SelectTrigger>
                <SelectValue placeholder="Select region" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Regions</SelectItem>
                <SelectItem value="asia">Asia Pacific</SelectItem>
                <SelectItem value="europe">Europe</SelectItem>
                <SelectItem value="americas">Americas</SelectItem>
                <SelectItem value="africa">Africa & Middle East</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Year */}
          <div className="space-y-3">
            <Label className="text-sm text-muted-foreground">Year Range</Label>
            <Select defaultValue="all">
              <SelectTrigger>
                <SelectValue placeholder="Select year range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Years</SelectItem>
                <SelectItem value="2020s">2020–Present</SelectItem>
                <SelectItem value="2010s">2010–2019</SelectItem>
                <SelectItem value="2000s">2000–2009</SelectItem>
                <SelectItem value="1990s">1990–1999</SelectItem>
                <SelectItem value="pre1990">Before 1990</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Disaster Cards Grid */}
      {disasters.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {disasters.map((disaster, i) => (
            <div
              key={i}
              className="content-card hover:border-primary/30 transition-colors cursor-pointer group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                    {disaster.case_study_id || "Unknown Event"}
                  </h3>
                  <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {/* Fallback for year since we don't have explicit date field yet */}
                      {disaster.inferred_time_window.substring(0, 20)}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {disaster.location_context?.substring(0, 15) || "Unknown"}...
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-primary">
                    {Math.round(disaster.similarity_score * 100)}%
                  </div>
                  <div className="text-xs text-muted-foreground">similarity</div>
                </div>
              </div>

              {/* Magnitude Badge (Mocked for now as not in snapshot) */}
              <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-secondary text-xs font-medium text-foreground mb-4">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                Severity: High
              </div>

              {/* Risks / Failure Modes */}
              <div className="mb-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-red-600 mb-2 flex items-center gap-1">
                  <XCircle className="h-3 w-3" />
                  Key Risks
                </p>
                <ul className="space-y-1">
                  {disaster.risks_perceived?.slice(0, 3).map((risk, j) => (
                    <li key={j} className="text-xs text-muted-foreground pl-4 relative before:content-['–'] before:absolute before:left-1 truncate">
                      {risk}
                    </li>
                  )) || <li>No risks recorded</li>}
                </ul>
              </div>

              {/* Actions / Successes */}
              <div className="mb-4">
                <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600 mb-2 flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  Actions Taken
                </p>
                <div className="text-xs text-muted-foreground pl-4 relative before:content-['–'] before:absolute before:left-1 line-clamp-3">
                  {disaster.action_taken_narrative || "No actions recorded"}
                </div>
              </div>

              {/* Expand Indicator */}
              <div className="flex items-center justify-center pt-2 border-t border-border">
                <span className="text-xs text-muted-foreground flex items-center gap-1 group-hover:text-primary transition-colors">
                  View Full Snapshot
                  <ChevronDown className="h-3 w-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <AlertCircle className="w-10 h-10 mb-2 opacity-20" />
          <p>No historical data found.</p>
          <p className="text-xs mt-1">Try ingesting case studies first.</p>
        </div>
      )}
    </div>
  );
}
