"use client"

import { SourceHealthCard } from '@/components/dashboard/source-health-card'
import { LiveExtractionFeed } from '@/components/dashboard/live-extraction-feed'
import { QualityScoreGauge } from '@/components/dashboard/quality-score-gauge'
import { PipelineHealthCard } from '@/components/dashboard/pipeline-health-card'
import { RecentJobsCard } from '@/components/dashboard/recent-jobs-card'
import { ExportStatsCard } from '@/components/dashboard/export-stats-card'

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Pulse</h1>
          <p className="text-muted-foreground mt-2">
            Real-time health and performance of your 6-layer DataOps pipeline
          </p>
        </div>
      </div>

      {/* Bento Grid Layout */}
      <div className="bento-grid">
        {/* Row 1 */}
        <SourceHealthCard />
        <LiveExtractionFeed />
        <QualityScoreGauge />

        {/* Row 2 */}
        <PipelineHealthCard />
        <RecentJobsCard />
        <ExportStatsCard />
      </div>
    </div>
  )
}