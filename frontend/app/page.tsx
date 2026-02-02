"use client"

import { ActiveTaskMonitor } from "@/components/dashboard/ActiveTask"
import { SelectorTester } from "@/components/dashboard/SelectorTester"
import { JobOverview } from "@/components/dashboard/JobOverview"
import { RecentLogs } from "@/components/dashboard/RecentLogs"
import { Badge } from "@/components/ui/badge"
import { Users, MoreHorizontal } from "lucide-react"

export default function Dashboard() {
  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold font-outfit tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back, verified user.</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/20 px-3 py-1">
            System Healthy
          </Badge>
          <div className="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center">
            <Users className="h-4 w-4" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">

        {/* Left Column (Main) */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <ActiveTaskMonitor />
          <JobOverview />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-6 min-h-[200px] flex items-center justify-center border-dashed border-2 border-white/10">
              <p className="text-muted-foreground text-sm">Analytics Chart Placeholder</p>
            </div>
            <RecentLogs />
          </div>
        </div>

        {/* Right Column (Tools) */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <SelectorTester />

          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold font-outfit">AI Schema Diff</h3>
              <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-white/5 border border-white/5 text-sm">
                <div className="flex justify-between mb-1">
                  <span className="font-mono text-xs text-red-400">- .product_price</span>
                  <span className="text-[10px] text-muted-foreground">Removed</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-mono text-xs text-green-400">+ .price_display</span>
                  <span className="text-[10px] text-muted-foreground">Added</span>
                </div>
              </div>
              <Badge variant="outline" className="w-full justify-center py-1.5 cursor-pointer hover:bg-white/5">
                View Changes
              </Badge>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}