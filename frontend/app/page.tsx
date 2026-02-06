"use client"
import React from 'react'

import { SystemStatus } from "@/components/dashboard/SystemStatus"
import { AISchemaBuilder } from "@/components/dashboard/AISchemaBuilder"
import { IntelligenceFeed } from "@/components/dashboard/IntelligenceFeed"
import { StatsGrid } from "@/components/dashboard/StatsGrid"

export default function Dashboard() {
  return (
    <div className="space-y-6 pt-6 animate-in">
      <div className="text-center md:text-left mb-4 text-xs text-muted-foreground uppercase tracking-widest font-mono">
        {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
      </div>

      <div className="stagger-1">
        <SystemStatus />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 stagger-2">
        <div className="lg:col-span-7">
          <AISchemaBuilder />
        </div>
        <div className="lg:col-span-5">
          <IntelligenceFeed />
        </div>
      </div>

      <div className="stagger-3">
        <StatsGrid />
      </div>
    </div>
  )
}
