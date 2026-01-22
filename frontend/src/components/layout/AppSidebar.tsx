import { NavLink, useLocation } from "react-router-dom";
import {
  Terminal,
  LayoutDashboard,
  Clock,
  History,
  Lightbulb,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  {
    title: "Input Console",
    href: "/input-console",
    icon: Terminal,
    description: "Data entry and system inputs",
  },
  {
    title: "Situation Dashboard",
    href: "/situation-dashboard",
    icon: LayoutDashboard,
    description: "Current situation overview",
  },
  {
    title: "24–48 Hour Timeline",
    href: "/timeline",
    icon: Clock,
    description: "Projected event timeline",
  },
  {
    title: "Similar Past Disasters",
    href: "/past-disasters",
    icon: History,
    description: "Historical comparison data",
  },
  {
    title: "Insights & Recommendations",
    href: "/insights",
    icon: Lightbulb,
    description: "AI-generated recommendations",
  },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <aside className="flex h-screen w-64 flex-col bg-sidebar border-r border-sidebar-border">
      {/* Logo / Brand */}
      <div className="flex items-center gap-3 border-b border-sidebar-border px-4 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-primary">
          <Shield className="h-5 w-5 text-sidebar-primary-foreground" />
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-medium uppercase tracking-wider text-sidebar-muted">
            DIS
          </span>
          <span className="text-xs text-sidebar-foreground/60">v2.4.1</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <div className="mb-3 px-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-sidebar-muted">
            Navigation
          </span>
        </div>
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <NavLink
              key={item.href}
              to={item.href}
              className={cn(
                "nav-item",
                isActive && "nav-item-active"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              <span>{item.title}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-sidebar-border px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse-subtle" />
          <span className="text-xs text-sidebar-foreground/60">
            System Operational
          </span>
        </div>
      </div>
    </aside>
  );
}
