"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Shield,
  LayoutDashboard,
  Globe,
  Search,
  Settings,
  Zap,
  Layers,
  Activity
} from "lucide-react"

const NAV_ITEMS = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/" },
  { label: "Jobs", icon: Globe, href: "/jobs" },
  { label: "Scraper Engine", icon: Search, href: "/scrape" },
  { label: "Review Data", icon: Shield, href: "/review" },
  { label: "Settings", icon: Settings, href: "/settings" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="h-screen w-64 border-r border-white/10 flex flex-col glass fixed left-0 top-0 z-50">
      <div className="p-6">
        <div className="flex items-center gap-3 px-2 mb-8">
          <div className="h-8 w-8 bg-primary/20 border border-primary/30 rounded-lg flex items-center justify-center">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <span className="font-bold font-outfit text-xl tracking-tight">
            Scraper<span className="text-primary">Pro</span>
          </span>
        </div>

        <div className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`sidebar-item group relative overflow-hidden ${isActive ? "premium-glow text-white" : "text-muted-foreground hover:text-white"}`}
              >
                <div className={`absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent opacity-0 transition-opacity duration-300 ${isActive ? "opacity-100" : "group-hover:opacity-50"}`} />
                <item.icon className={`h-4 w-4 relative z-10 transition-colors ${isActive ? "text-primary-foreground" : "group-hover:text-primary"}`} />
                <span className="text-sm font-medium relative z-10">{item.label}</span>
                {isActive && (
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 h-8 w-1 bg-primary rounded-l-full shadow-[0_0_10px_rgba(124,58,237,0.8)]" />
                )}
              </Link>
            )
          })}
        </div>
      </div>

      <div className="mt-auto p-6">
        <div className="p-4 rounded-xl bg-gradient-to-br from-primary/10 to-purple-500/10 border border-primary/20">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-4 w-4 text-primary" />
            <span className="text-xs font-bold uppercase tracking-wider text-primary">Pro Plan</span>
          </div>
          <p className="text-xs text-muted-foreground mb-3">
            Using 14% of monthly quota
          </p>
          <div className="h-1.5 w-full bg-black/40 rounded-full overflow-hidden">
            <div className="h-full w-[14%] bg-primary rounded-full" />
          </div>
        </div>
      </div>
    </div>
  )
}
