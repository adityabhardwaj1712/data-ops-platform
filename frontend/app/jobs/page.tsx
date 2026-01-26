"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Play,
  Pause,
  Square,
  Trash2,
  Eye,
  Download,
  Settings,
  Clock,
  CheckCircle,
  AlertTriangle,
  Zap
} from 'lucide-react'

interface Job {
  id: string
  name: string
  description: string
  status: 'running' | 'paused' | 'completed' | 'failed' | 'queued'
  progress: number
  recordsProcessed: number
  totalRecords: number
  startedAt: Date
  estimatedCompletion?: Date
  errorMessage?: string
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([
    {
      id: '1',
      name: 'DevOps Jobs Scraper',
      description: 'Extract DevOps job listings from LinkedIn, Indeed, and Glassdoor',
      status: 'running',
      progress: 75,
      recordsProcessed: 234,
      totalRecords: 300,
      startedAt: new Date(Date.now() - 1000 * 60 * 45),
      estimatedCompletion: new Date(Date.now() + 1000 * 60 * 15)
    },
    {
      id: '2',
      name: 'Product Manager Roles',
      description: 'Find PM positions in tech companies',
      status: 'completed',
      progress: 100,
      recordsProcessed: 156,
      totalRecords: 156,
      startedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
    },
    {
      id: '3',
      name: 'Frontend Developer Jobs',
      description: 'React and Vue.js positions across major cities',
      status: 'failed',
      progress: 45,
      recordsProcessed: 89,
      totalRecords: 200,
      startedAt: new Date(Date.now() - 1000 * 60 * 60 * 4),
      errorMessage: 'CAPTCHA detection triggered - operation paused'
    },
    {
      id: '4',
      name: 'Data Science Weekly',
      description: 'Weekly scan for new data science positions',
      status: 'paused',
      progress: 30,
      recordsProcessed: 67,
      totalRecords: 220,
      startedAt: new Date(Date.now() - 1000 * 60 * 60 * 6),
    },
    {
      id: '5',
      name: 'UX Designer Roles',
      description: 'Creative design positions in design agencies',
      status: 'queued',
      progress: 0,
      recordsProcessed: 0,
      totalRecords: 0,
      startedAt: new Date(),
    }
  ])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Play className="h-4 w-4 text-blue-500" />
      case 'paused':
        return <Pause className="h-4 w-4 text-yellow-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'queued':
        return <Clock className="h-4 w-4 text-gray-500" />
      default:
        return <Play className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30'
      case 'paused':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/30'
      case 'failed':
        return 'bg-red-500/10 text-red-400 border-red-500/30'
      case 'queued':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/30'
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/30'
    }
  }

  const formatDuration = (startDate: Date, endDate?: Date) => {
    const end = endDate || new Date()
    const diff = end.getTime() - startDate.getTime()
    const minutes = Math.floor(diff / (1000 * 60))

    if (minutes < 60) return `${minutes}m`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ${minutes % 60}m`
  }

  const handleJobAction = (jobId: string, action: 'start' | 'pause' | 'stop' | 'delete') => {
    setJobs(prev => prev.map(job => {
      if (job.id === jobId) {
        switch (action) {
          case 'start':
            return { ...job, status: 'running' as const }
          case 'pause':
            return { ...job, status: 'paused' as const }
          case 'stop':
            return { ...job, status: 'completed' as const }
          case 'delete':
            return null
          default:
            return job
        }
      }
      return job
    }).filter(Boolean) as Job[])
  }

  const runningJobs = jobs.filter(j => j.status === 'running').length
  const completedJobs = jobs.filter(j => j.status === 'completed').length
  const failedJobs = jobs.filter(j => j.status === 'failed').length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Job Management</h1>
          <p className="text-muted-foreground mt-2">
            Monitor and control your data scraping operations
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
            {runningJobs} Running
          </Badge>
          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
            {completedJobs} Completed
          </Badge>
          <Badge variant="outline" className="bg-red-500/10 text-red-400 border-red-500/30">
            {failedJobs} Failed
          </Badge>
          <Button>
            <Zap className="h-4 w-4 mr-2" />
            New Job
          </Button>
        </div>
      </div>

      {/* Job Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Jobs</p>
                <p className="text-2xl font-bold">{jobs.length}</p>
              </div>
              <Zap className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Now</p>
                <p className="text-2xl font-bold text-blue-400">{runningJobs}</p>
              </div>
              <Play className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold text-green-400">
                  {Math.round((completedJobs / Math.max(jobs.length - runningJobs, 1)) * 100)}%
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="premium-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Records</p>
                <p className="text-2xl font-bold">
                  {jobs.reduce((sum, job) => sum + job.recordsProcessed, 0).toLocaleString()}
                </p>
              </div>
              <Download className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Jobs List */}
      <Card className="premium-card">
        <CardHeader>
          <CardTitle>Active Jobs</CardTitle>
          <CardDescription>
            Real-time status of all scraping operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="border border-border rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-4">
                    <div className="mt-1">
                      {getStatusIcon(job.status)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{job.name}</h3>
                      <p className="text-muted-foreground text-sm mt-1">{job.description}</p>
                    </div>
                  </div>

                  <Badge variant="outline" className={getStatusColor(job.status)}>
                    {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                  </Badge>
                </div>

                {/* Progress and Stats */}
                <div className="space-y-3 mb-4">
                  {job.status === 'running' && (
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progress</span>
                        <span>{job.progress}%</span>
                      </div>
                      <Progress value={job.progress} className="h-2" />
                    </div>
                  )}

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Records:</span>
                      <span className="ml-2 font-medium">
                        {job.recordsProcessed.toLocaleString()}
                        {job.totalRecords > 0 && ` / ${job.totalRecords.toLocaleString()}`}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="ml-2 font-medium">
                        {formatDuration(job.startedAt)}
                      </span>
                    </div>
                    {job.estimatedCompletion && job.status === 'running' && (
                      <div>
                        <span className="text-muted-foreground">ETA:</span>
                        <span className="ml-2 font-medium">
                          {formatDuration(new Date(), job.estimatedCompletion)}
                        </span>
                      </div>
                    )}
                    <div>
                      <span className="text-muted-foreground">Started:</span>
                      <span className="ml-2 font-medium">
                        {job.startedAt.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {job.errorMessage && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-md p-3 mb-4">
                    <p className="text-red-400 text-sm">{job.errorMessage}</p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center space-x-2">
                  {job.status === 'running' && (
                    <>
                      <Button variant="outline" size="sm" onClick={() => handleJobAction(job.id, 'pause')}>
                        <Pause className="h-4 w-4 mr-1" />
                        Pause
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleJobAction(job.id, 'stop')}>
                        <Square className="h-4 w-4 mr-1" />
                        Stop
                      </Button>
                    </>
                  )}

                  {job.status === 'paused' && (
                    <Button variant="outline" size="sm" onClick={() => handleJobAction(job.id, 'start')}>
                      <Play className="h-4 w-4 mr-1" />
                      Resume
                    </Button>
                  )}

                  {job.status === 'queued' && (
                    <Button variant="outline" size="sm" onClick={() => handleJobAction(job.id, 'start')}>
                      <Play className="h-4 w-4 mr-1" />
                      Start
                    </Button>
                  )}

                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>

                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-1" />
                    Export
                  </Button>

                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-1" />
                    Config
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleJobAction(job.id, 'delete')}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}