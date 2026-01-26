"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PlayCircle, PauseCircle, CheckCircle, XCircle, ExternalLink } from 'lucide-react'

interface Job {
  id: string
  description: string
  status: 'running' | 'completed' | 'failed' | 'paused'
  progress: number
  records: number
  startedAt: Date
  estimatedTime: number
}

export function RecentJobsCard() {
  const [jobs] = useState<Job[]>([
    {
      id: '1',
      description: 'DevOps Job Listings - India',
      status: 'running',
      progress: 75,
      records: 234,
      startedAt: new Date(Date.now() - 1000 * 60 * 15),
      estimatedTime: 1800000 // 30 minutes
    },
    {
      id: '2',
      description: 'React Developer Positions',
      status: 'completed',
      progress: 100,
      records: 156,
      startedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
      estimatedTime: 900000
    },
    {
      id: '3',
      description: 'Data Science Roles - Remote',
      status: 'failed',
      progress: 45,
      records: 89,
      startedAt: new Date(Date.now() - 1000 * 60 * 60 * 4),
      estimatedTime: 1200000
    },
    {
      id: '4',
      description: 'Product Manager Jobs',
      status: 'paused',
      progress: 30,
      records: 67,
      startedAt: new Date(Date.now() - 1000 * 60 * 60 * 6),
      estimatedTime: 1500000
    }
  ])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <PlayCircle className="h-3 w-3 text-blue-500" />
      case 'completed':
        return <CheckCircle className="h-3 w-3 text-green-500" />
      case 'failed':
        return <XCircle className="h-3 w-3 text-red-500" />
      case 'paused':
        return <PauseCircle className="h-3 w-3 text-yellow-500" />
      default:
        return <PlayCircle className="h-3 w-3 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30'
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/30'
      case 'failed':
        return 'bg-red-500/10 text-red-400 border-red-500/30'
      case 'paused':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/30'
    }
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / (1000 * 60))

    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ago`
  }

  const runningJobs = jobs.filter(j => j.status === 'running').length

  return (
    <Card className="premium-card glow-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Recent Jobs</CardTitle>
            <CardDescription>
              Latest scraping operations
            </CardDescription>
          </div>
          <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
            {runningJobs} Active
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {jobs.map((job) => (
            <div key={job.id} className="p-3 rounded-md bg-muted/50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(job.status)}
                  <span className="text-sm font-medium truncate">
                    {job.description}
                  </span>
                </div>
                <Badge variant="outline" className={`text-xs ${getStatusColor(job.status)}`}>
                  {job.status}
                </Badge>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
                <span>{job.records} records</span>
                <span>{formatTime(job.startedAt)}</span>
              </div>

              {job.status === 'running' && (
                <div className="w-full bg-muted rounded-full h-1.5 mb-2">
                  <div
                    className="bg-primary h-1.5 rounded-full transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              )}

              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  {job.status === 'running' ? `${job.progress}% complete` : `${job.records} records processed`}
                </span>
                <Button variant="ghost" size="sm" className="h-6 px-2">
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-3 border-t border-border">
          <Button variant="outline" className="w-full" size="sm">
            View All Jobs
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}