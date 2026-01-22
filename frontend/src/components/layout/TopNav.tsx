import { Bell, Radio } from "lucide-react";

export function TopNav() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-foreground">
          Disaster Intelligence System
        </h1>
        <div className="hidden items-center gap-2 rounded-full bg-secondary px-3 py-1 sm:flex">
          <Radio className="h-3 w-3 text-emerald-600" />
          <span className="text-xs font-medium text-secondary-foreground">
            Live Feed Active
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Current Time */}
        <div className="hidden text-right md:block">
          <p className="text-xs text-muted-foreground">Local Time</p>
          <p className="text-sm font-medium text-foreground tabular-nums">
            {new Date().toLocaleTimeString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
              hour12: false,
            })}{" "}
            UTC
          </p>
        </div>

        {/* Notifications */}
        <button className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-background transition-colors hover:bg-secondary">
          <Bell className="h-4 w-4 text-muted-foreground" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground">
            3
          </span>
        </button>

        {/* User */}
        <div className="flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-1.5">
          <div className="h-6 w-6 rounded-full bg-primary" />
          <span className="text-sm font-medium text-foreground">Operator</span>
        </div>
      </div>
    </header>
  );
}
