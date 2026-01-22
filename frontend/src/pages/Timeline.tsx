import { CloudRain, Zap, Gauge, ChevronRight } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

const timeMarkers = [
  {
    label: "Now",
    time: "14:00",
    impacts: [
      "Active seismic tremors detected",
      "Primary infrastructure damage reported",
      "Emergency shelters at 45% capacity",
    ],
    mitigations: [
      "Deploy search and rescue teams to Zone A",
      "Activate emergency communication channels",
      "Begin evacuation of high-risk areas",
    ],
    confidence: 98,
  },
  {
    label: "6 Hours",
    time: "20:00",
    impacts: [
      "Aftershock probability peaks at 65%",
      "Flooding expected in low-lying sectors",
      "Power grid stress in North District",
    ],
    mitigations: [
      "Pre-position medical teams at shelters",
      "Deploy flood barriers to vulnerable areas",
      "Activate backup power generators",
    ],
    confidence: 92,
  },
  {
    label: "12 Hours",
    time: "02:00",
    impacts: [
      "Secondary building collapses possible",
      "Road network degradation increases",
      "Water supply contamination risk",
    ],
    mitigations: [
      "Structural assessment of critical buildings",
      "Establish alternative transport routes",
      "Distribute emergency water supplies",
    ],
    confidence: 85,
  },
  {
    label: "24 Hours",
    time: "14:00 +1d",
    impacts: [
      "Aftershock intensity decreases",
      "Shelter capacity reaches limit",
      "Supply chain disruptions persist",
    ],
    mitigations: [
      "Transition to recovery operations",
      "Activate overflow shelter facilities",
      "Coordinate regional supply logistics",
    ],
    confidence: 78,
  },
  {
    label: "48 Hours",
    time: "14:00 +2d",
    impacts: [
      "Situation stabilization expected",
      "Infrastructure assessment complete",
      "Displaced population peaks",
    ],
    mitigations: [
      "Begin systematic damage documentation",
      "Initiate infrastructure repair planning",
      "Establish long-term housing solutions",
    ],
    confidence: 65,
  },
];

export default function Timeline() {
  return (
    <div className="p-6">
      <div className="page-header mb-6 -mx-6 -mt-6 px-6 py-4">
        <h1 className="page-title">24–48 Hour Timeline</h1>
        <p className="page-subtitle">
          Visualize predicted impacts and mitigation measures over time
        </p>
      </div>

      {/* Controls */}
      <div className="content-card mb-6">
        <div className="flex flex-wrap items-center gap-8">
          {/* Toggle Switches */}
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Switch id="heavy-rain" defaultChecked />
              <Label htmlFor="heavy-rain" className="flex items-center gap-1.5 text-sm cursor-pointer">
                <CloudRain className="h-4 w-4 text-blue-500" />
                Heavy Rain
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch id="aftershocks" defaultChecked />
              <Label htmlFor="aftershocks" className="flex items-center gap-1.5 text-sm cursor-pointer">
                <Zap className="h-4 w-4 text-amber-500" />
                Aftershocks
              </Label>
            </div>
          </div>

          {/* Divider */}
          <div className="hidden sm:block h-8 w-px bg-border" />

          {/* Uncertainty Slider */}
          <div className="flex items-center gap-4 flex-1 min-w-[280px]">
            <div className="flex items-center gap-1.5">
              <Gauge className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground whitespace-nowrap">Uncertainty:</span>
            </div>
            <div className="flex items-center gap-3 flex-1">
              <span className="text-xs text-muted-foreground">Conservative</span>
              <Slider defaultValue={[50]} max={100} step={1} className="flex-1" />
              <span className="text-xs text-muted-foreground">Aggressive</span>
            </div>
          </div>
        </div>
      </div>

      {/* Horizontal Timeline */}
      <div className="content-card overflow-x-auto">
        {/* Timeline Bar */}
        <div className="relative min-w-[900px]">
          {/* Line */}
          <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" />
          
          {/* Markers */}
          <div className="relative flex justify-between">
            {timeMarkers.map((marker, i) => (
              <div key={i} className="flex flex-col items-center" style={{ width: '18%' }}>
                {/* Marker Point */}
                <div
                  className={`relative z-10 flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                    i === 0
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-background text-muted-foreground hover:border-primary/50"
                  }`}
                >
                  <span className="text-xs font-bold">{i === 0 ? "●" : `+${i * (i < 3 ? 6 : i === 3 ? 12 : 24)}h`}</span>
                </div>
                
                {/* Label */}
                <div className="mt-2 text-center">
                  <p className="text-sm font-semibold text-foreground">{marker.label}</p>
                  <p className="text-xs text-muted-foreground">{marker.time}</p>
                </div>

                {/* Expandable Card */}
                <div className="mt-4 w-full rounded-lg border border-border bg-card p-4 hover:border-primary/30 transition-colors">
                  {/* Confidence Indicator */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      Confidence
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-12 rounded-full bg-secondary overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            marker.confidence >= 90
                              ? "bg-emerald-500"
                              : marker.confidence >= 75
                              ? "bg-amber-500"
                              : "bg-orange-500"
                          }`}
                          style={{ width: `${marker.confidence}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-foreground">{marker.confidence}%</span>
                    </div>
                  </div>

                  {/* Predicted Impacts */}
                  <div className="mb-3">
                    <p className="text-xs font-semibold text-red-600 uppercase tracking-wider mb-1.5">
                      Predicted Impacts
                    </p>
                    <ul className="space-y-1">
                      {marker.impacts.map((impact, j) => (
                        <li key={j} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                          <ChevronRight className="h-3 w-3 mt-0.5 shrink-0 text-red-500" />
                          {impact}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommended Mitigations */}
                  <div>
                    <p className="text-xs font-semibold text-emerald-600 uppercase tracking-wider mb-1.5">
                      Mitigations
                    </p>
                    <ul className="space-y-1">
                      {marker.mitigations.map((mitigation, j) => (
                        <li key={j} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                          <ChevronRight className="h-3 w-3 mt-0.5 shrink-0 text-emerald-500" />
                          {mitigation}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
