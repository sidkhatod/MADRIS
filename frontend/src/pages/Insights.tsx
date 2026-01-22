import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  Download,
  Shield,
  Users,
  Building,
  Zap,
  FileText,
  History,
  TrendingUp,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, DecisionSupportResponse } from "@/lib/api";

export default function Insights() {
  const [data, setData] = useState<DecisionSupportResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // In a real app, this would pick up the "current narrative" from context/state
        // For now, we simulate a context trigger or use a default if coming from "Process"
        const currentNarrative =
          "Massive earthquake detected in urban center. Early reports indicate structural damage to older masonry buildings and potential liquefaction zones near the harbor. Communication is intermittent.";

        const response = await api.post<DecisionSupportResponse>(
          "/reasoning/decision-support",
          { current_narrative: currentNarrative }
        );
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch insights:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // Fallback if API fails or returns empty lists
  const topRisks = data?.top_risks.map((risk, index) => ({
    rank: index + 1,
    title: risk.length > 50 ? risk.substring(0, 50) + "..." : risk,
    severity: index === 0 ? "critical" : index < 3 ? "high" : "medium",
    description: risk, // Using the risk text itself as description
    icon: index === 0 ? AlertTriangle : TrendingUp,
  })) || [];

  const recommendedActions = data?.recommended_actions.map((action, index) => ({
    rank: index + 1,
    title: action.length > 50 ? action.substring(0, 50) + "..." : action,
    priority: index === 0 ? "critical" : index < 3 ? "high" : "medium",
    description: action,
    icon: Shield,
  })) || [];

  return (
    <div className="p-6">
      <div className="page-header mb-6 -mx-6 -mt-6 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Insights & Recommendations</h1>
            <p className="page-subtitle">
              Key risks and recommended actions for decision-makers
            </p>
          </div>
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Export Snapshot
          </Button>
        </div>
      </div>

      {/* Two-Column Layout */}
      <div className="grid gap-6 lg:grid-cols-2 mb-6">
        {/* Left: Top Risks */}
        <div className="content-card">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <h2 className="text-lg font-semibold text-foreground">Top Risks</h2>
            <span className="ml-auto text-xs text-muted-foreground">Ranked by severity</span>
          </div>
          {topRisks.length > 0 ? (
            <div className="space-y-4">
              {topRisks.map((risk) => (
                <div
                  key={risk.rank}
                  className={`flex gap-4 p-3 rounded-lg border ${risk.severity === "critical"
                      ? "border-red-500/30 bg-red-500/5"
                      : risk.severity === "high"
                        ? "border-amber-500/30 bg-amber-500/5"
                        : "border-border bg-secondary/30"
                    }`}
                >
                  <div className="flex flex-col items-center gap-1">
                    <span className={`text-lg font-bold ${risk.severity === "critical"
                        ? "text-red-600"
                        : risk.severity === "high"
                          ? "text-amber-600"
                          : "text-muted-foreground"
                      }`}>
                      #{risk.rank}
                    </span>
                    <risk.icon className={`h-4 w-4 ${risk.severity === "critical"
                        ? "text-red-500"
                        : risk.severity === "high"
                          ? "text-amber-500"
                          : "text-muted-foreground"
                      }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-medium text-foreground text-sm">
                        {risk.title}
                      </h3>
                      <span className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium uppercase ${risk.severity === "critical"
                          ? "bg-red-500/20 text-red-600"
                          : risk.severity === "high"
                            ? "bg-amber-500/20 text-amber-600"
                            : "bg-secondary text-muted-foreground"
                        }`}>
                        {risk.severity}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {risk.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No specific risks identified yet.
            </div>
          )}
        </div>

        {/* Right: Recommended Actions */}
        <div className="content-card">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border">
            <CheckCircle className="h-5 w-5 text-emerald-500" />
            <h2 className="text-lg font-semibold text-foreground">Recommended Actions</h2>
            <span className="ml-auto text-xs text-muted-foreground">Ranked by priority</span>
          </div>
          {recommendedActions.length > 0 ? (
            <div className="space-y-4">
              {recommendedActions.map((action) => (
                <div
                  key={action.rank}
                  className={`flex gap-4 p-3 rounded-lg border ${action.priority === "critical"
                      ? "border-emerald-500/30 bg-emerald-500/5"
                      : action.priority === "high"
                        ? "border-primary/30 bg-primary/5"
                        : "border-border bg-secondary/30"
                    }`}
                >
                  <div className="flex flex-col items-center gap-1">
                    <span className={`text-lg font-bold ${action.priority === "critical"
                        ? "text-emerald-600"
                        : action.priority === "high"
                          ? "text-primary"
                          : "text-muted-foreground"
                      }`}>
                      #{action.rank}
                    </span>
                    <action.icon className={`h-4 w-4 ${action.priority === "critical"
                        ? "text-emerald-500"
                        : action.priority === "high"
                          ? "text-primary"
                          : "text-muted-foreground"
                      }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-medium text-foreground text-sm">
                        {action.title}
                      </h3>
                      <span className={`shrink-0 px-2 py-0.5 rounded text-xs font-medium uppercase ${action.priority === "critical"
                          ? "bg-emerald-500/20 text-emerald-600"
                          : action.priority === "high"
                            ? "bg-primary/20 text-primary"
                            : "bg-secondary text-muted-foreground"
                        }`}>
                        {action.priority}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {action.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No specific actions recommended yet.
            </div>
          )}
        </div>
      </div>

      {/* Explainability Panel */}
      <div className="content-card bg-secondary/30">
        <div className="flex items-center gap-2 mb-4">
          <History className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold text-foreground">Recommendation Explainability</h2>
        </div>
        <div className="rounded-lg border border-border bg-background p-4">
          <div className="flex items-start gap-3">
            <FileText className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
            <div className="space-y-3 text-sm text-muted-foreground">
              {data?.explanation ? (
                <div className="whitespace-pre-wrap">{data.explanation}</div>
              ) : (
                <p>Generating analysis...</p>
              )}

              {data && data.historical_basis.length > 0 && (
                <>
                  <p className="pt-2 border-t border-border mt-3">
                    <span className="font-medium text-foreground">Historical Basis:</span> Derived from {data.historical_basis.length} similar case studies (Avg Similarity: {Math.round(data.historical_basis.reduce((acc, curr) => acc + curr.similarity_score, 0) / data.historical_basis.length * 100)}%).
                  </p>
                  {/* Explicitly omit the previous hardcoded list unless we want to map historical_basis to it */}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
