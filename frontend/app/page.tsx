"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  Zap,
  Database,
  Globe
} from 'lucide-react'
import { api } from '@/lib/api'

interface DashboardStats {
  total_jobs: number
  running_jobs: number
  completed_jobs: number
  failed_jobs: number
  success_rate: number
  avg_confidence: number
}

export default function EnhancedDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const data = await api.get<any>('/api/analytics/dashboard')
      setStats({
        total_jobs: data.total_jobs || 0,
        running_jobs: data.running_jobs || 0,
        completed_jobs: data.completed_jobs || 0,
        failed_jobs: data.failed_jobs || 0,
        success_rate: data.success_rate || 0,
        avg_confidence: data.avg_confidence || 0,
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Pulse</h1>
        <p className="text-muted-foreground mt-2">
          Real-time health and performance of your 6-layer DataOps pipeline
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_jobs || 0}</div>
            <p className="text-xs text-muted-foreground">
              All time scraping jobs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running</CardTitle>
            <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">
              {stats?.running_jobs || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently processing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {stats?.success_rate?.toFixed(1) || 0}%
            </div>
            <Progress value={stats?.success_rate || 0} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-500">
              {(stats?.avg_confidence * 100)?.toFixed(0) || 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Data quality score
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common scraping tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <a
              href="/scrape"
              className="flex items-center p-4 border rounded-lg hover:bg-accent transition-colors cursor-pointer"
            >
              <Globe className="h-8 w-8 mr-4 text-primary" />
              <div>
                <h3 className="font-semibold">New Scrape</h3>
                <p className="text-sm text-muted-foreground">Start scraping</p>
              </div>
            </a>

            <a
              href="/jobs"
              className="flex items-center p-4 border rounded-lg hover:bg-accent transition-colors cursor-pointer"
            >
              <Activity className="h-8 w-8 mr-4 text-blue-500" />
              <div>
                <h3 className="font-semibold">View Jobs</h3>
                <p className="text-sm text-muted-foreground">Manage jobs</p>
              </div>
            </a>

            <a
              href="/pipeline"
              className="flex items-center p-4 border rounded-lg hover:bg-accent transition-colors cursor-pointer"
            >
              <Zap className="h-8 w-8 mr-4 text-yellow-500" />
              <div>
                <h3 className="font-semibold">Run Pipeline</h3>
                <p className="text-sm text-muted-foreground">6-layer scraping</p>
              </div>
            </a>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest scraping jobs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between border-b pb-4 last:border-0">
                <div className="flex items-center space-x-4">
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="font-medium">Job #{i}</p>
                    <p className="text-sm text-muted-foreground">Completed 2 minutes ago</p>
                  </div>
                </div>
                <Badge>Completed</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}