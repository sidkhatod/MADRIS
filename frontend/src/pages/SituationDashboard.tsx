import {
  Activity,
  Users,
  Building2,
  TrendingUp,
  AlertTriangle,
  MapPin,
  Clock,
  Layers,
  Radio,
} from "lucide-react";

const metrics = [
  {
    label: "Estimated Damage Index",
    value: "7.4",
    subtext: "Severe",
    icon: Activity,
    color: "text-red-600",
    bgColor: "bg-red-500/10",
  },
  {
    label: "Population Affected",
    value: "127,450",
    subtext: "Across 4 sectors",
    icon: Users,
    color: "text-foreground",
    bgColor: "bg-secondary",
  },
  {
    label: "Hospitals at Risk",
    value: "12",
    subtext: "Of 34 in region",
    icon: Building2,
    color: "text-amber-600",
    bgColor: "bg-amber-500/10",
  },
  {
    label: "Aftershock Probability",
    value: "68%",
    subtext: "Next 48 hours",
    icon: TrendingUp,
    color: "text-amber-600",
    bgColor: "bg-amber-500/10",
  },
];

const mapLayers = [
  { name: "Seismic Intensity", color: "bg-red-500", active: true },
  { name: "Fault Lines", color: "bg-orange-500", active: true },
  { name: "Population Density", color: "bg-blue-500", active: true },
  { name: "Critical Infrastructure", color: "bg-emerald-500", active: true },
];

const alerts = [
  {
    severity: "critical",
    message: "Aftershock M4.2 detected 12km NE of epicenter. Structural assessments recommended.",
    time: "2 min ago",
  },
  {
    severity: "warning",
    message: "Highway 45 bridge showing stress fractures. Reroute heavy vehicles immediately.",
    time: "18 min ago",
  },
  {
    severity: "warning",
    message: "Central Hospital backup generator at 40% capacity. Fuel resupply needed within 6 hours.",
    time: "34 min ago",
  },
  {
    severity: "info",
    message: "Search and Rescue Team Alpha reports sector B-7 cleared. Moving to B-8.",
    time: "45 min ago",
  },
];

export default function SituationDashboard() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">
            Situation Dashboard
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time situational awareness overview
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full bg-secondary px-3 py-1.5">
            <Radio className="h-3 w-3 text-emerald-600" />
            <span className="text-xs font-medium text-secondary-foreground">
              Live Data Feed
            </span>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Last Updated</p>
            <p className="text-sm font-medium text-foreground">2 min ago</p>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="content-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {metric.label}
                </p>
                <p className={`mt-1 text-3xl font-bold tabular-nums ${metric.color}`}>
                  {metric.value}
                </p>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {metric.subtext}
                </p>
              </div>
              <div className={`rounded-lg p-2.5 ${metric.bgColor}`}>
                <metric.icon className={`h-5 w-5 ${metric.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Map Section */}
      <div className="content-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-foreground">
            Operational Map View
          </h2>
          <div className="flex items-center gap-4">
            {mapLayers.map((layer) => (
              <div key={layer.name} className="flex items-center gap-2">
                <div className={`h-2.5 w-2.5 rounded-full ${layer.color}`} />
                <span className="text-xs text-muted-foreground">{layer.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Map Placeholder */}
        <div className="relative aspect-[21/9] rounded-lg bg-gradient-to-br from-slate-200 to-slate-300 overflow-hidden">
          {/* Grid overlay */}
          <div
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage:
                "linear-gradient(to right, #64748b 1px, transparent 1px), linear-gradient(to bottom, #64748b 1px, transparent 1px)",
              backgroundSize: "40px 40px",
            }}
          />

          {/* Center label */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Layers className="mx-auto mb-2 h-10 w-10 text-slate-400" />
              <p className="text-base font-semibold text-slate-500">
                Interactive Map Display
              </p>
              <p className="text-sm text-slate-400">
                GIS integration with layer overlays
              </p>
            </div>
          </div>

          {/* Simulated overlay zones */}
          <div className="absolute left-[15%] top-[25%] h-24 w-32 rounded-lg bg-red-500/20 border border-red-500/40" />
          <div className="absolute left-[35%] top-[40%] h-20 w-28 rounded-lg bg-orange-500/20 border border-orange-500/40" />
          <div className="absolute right-[25%] top-[30%] h-16 w-24 rounded-lg bg-amber-500/20 border border-amber-500/40" />

          {/* Fault line simulation */}
          <div className="absolute left-[10%] top-[60%] right-[30%] h-0.5 bg-orange-500/60 transform rotate-[-15deg]" />
          <div className="absolute left-[40%] top-[20%] right-[20%] h-0.5 bg-orange-500/40 transform rotate-[10deg]" />

          {/* Infrastructure markers */}
          <div className="absolute left-[20%] top-[35%] h-3 w-3 rounded-full bg-emerald-500 border-2 border-white shadow-md" />
          <div className="absolute left-[55%] top-[50%] h-3 w-3 rounded-full bg-emerald-500 border-2 border-white shadow-md" />
          <div className="absolute right-[35%] top-[25%] h-3 w-3 rounded-full bg-amber-500 border-2 border-white shadow-md animate-pulse-subtle" />
          <div className="absolute left-[30%] top-[55%] h-3 w-3 rounded-full bg-red-500 border-2 border-white shadow-md animate-pulse-subtle" />

          {/* Epicenter marker */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="relative">
              <div className="h-6 w-6 rounded-full bg-red-500 border-2 border-white shadow-lg flex items-center justify-center">
                <div className="h-2 w-2 rounded-full bg-white" />
              </div>
              <div className="absolute -inset-3 rounded-full border-2 border-red-500/40 animate-ping" />
            </div>
          </div>

          {/* Scale and coordinates */}
          <div className="absolute bottom-3 left-3 rounded bg-white/80 px-2 py-1 text-xs text-slate-600 backdrop-blur-sm">
            34.0522° N, 118.2437° W
          </div>
          <div className="absolute bottom-3 right-3 rounded bg-white/80 px-2 py-1 text-xs text-slate-600 backdrop-blur-sm">
            Scale: 1:50,000
          </div>
        </div>
      </div>

      {/* Bottom Section - Alerts & Event Details */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Time-Sensitive Alerts */}
        <div className="lg:col-span-2 content-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-foreground">
              Time-Sensitive Alerts
            </h2>
            <span className="status-indicator status-critical">
              <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse-subtle" />
              4 Active
            </span>
          </div>
          <div className="space-y-3">
            {alerts.map((alert, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 rounded-lg border p-3 ${
                  alert.severity === "critical"
                    ? "border-red-500/30 bg-red-500/5"
                    : alert.severity === "warning"
                    ? "border-amber-500/30 bg-amber-500/5"
                    : "border-border bg-background"
                }`}
              >
                <AlertTriangle
                  className={`h-4 w-4 shrink-0 mt-0.5 ${
                    alert.severity === "critical"
                      ? "text-red-500"
                      : alert.severity === "warning"
                      ? "text-amber-500"
                      : "text-muted-foreground"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-foreground">{alert.message}</p>
                  <p className="text-xs text-muted-foreground mt-1">{alert.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Event Metadata */}
        <div className="content-card">
          <h2 className="text-base font-semibold text-foreground mb-4">
            Event Details
          </h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-secondary p-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Location</p>
                <p className="text-sm font-medium text-foreground">
                  Central Valley Region
                </p>
                <p className="text-xs text-muted-foreground">
                  34.0522° N, 118.2437° W
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-secondary p-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Event Time</p>
                <p className="text-sm font-medium text-foreground">
                  Jan 21, 2026 • 06:32:18 UTC
                </p>
                <p className="text-xs text-muted-foreground">8 hours ago</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-secondary p-2">
                <Activity className="h-4 w-4 text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Magnitude</p>
                <p className="text-sm font-medium text-foreground">
                  M 6.4 (Mw)
                </p>
                <p className="text-xs text-muted-foreground">Depth: 12.3 km</p>
              </div>
            </div>

            <div className="border-t border-border pt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Event Type</span>
                <span className="font-medium text-foreground">Earthquake</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-muted-foreground">Alert Level</span>
                <span className="status-indicator status-critical">Red</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-muted-foreground">Response Phase</span>
                <span className="font-medium text-foreground">Active Response</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
