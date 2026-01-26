"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, AlertTriangle, Clock, ArrowRight } from 'lucide-react'

interface PipelineStage {
  id: string
  name: string
  status: 'completed' | 'running' | 'warning' | 'idle'
  progress: number
  duration: number
  records: number
}

export function PipelineHealthCard() {
  const [stages] = useState<PipelineStage[]>([
    { id: 'source', name: 'Source Intelligence', status: 'completed', progress: 100, duration: 1200, records: 450 },
    { id: 'fetch', name: 'Invisible Fetching', status: 'completed', progress: 100, duration: 8500, records: 445 },
    { id: 'clean', name: 'Content Cleaning', status: 'completed', progress: 100, duration: 3200, records: 445 },
    { id: 'extract', name: 'Intent Extraction', status: 'running', progress: 75, duration: 0, records: 334 },
    { id: 'quality', name: 'Quality Assurance', status: 'idle', progress: 0, duration: 0, records: 0 },
    { id: 'version', name: 'Version Storage', status: 'idle', progress: 0, duration: 0, records: 0 }
  ])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-3 w-3 text-green-500" />
      case 'running':
        return <div className="h-3 w-3 rounded-full bg-blue-500 animate-pulse" />
      case 'warning':
        return <AlertTriangle className="h-3 w-3 text-yellow-500" />
      default:
        return <Clock className="h-3 w-3 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-500/50 bg-green-500/10'
      case 'running':
        return 'border-blue-500/50 bg-blue-500/10'
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/10'
      default:
        return 'border-gray-500/50 bg-gray-500/10'
    }
  }

  const totalDuration = stages.reduce((sum, stage) => sum + stage.duration, 0)
  const totalRecords = Math.max(...stages.map(s => s.records))

  return (
    <Card className="premium-card glow-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Pipeline Health</CardTitle>
            <CardDescription>
              6-layer data processing status
            </CardDescription>
          </div>
          <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
            {totalRecords} Records
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {stages.map((stage, index) => (
            <div key={stage.id} className="relative">
              <div className={`flex items-center space-x-3 p-3 rounded-md border ${getStatusColor(stage.status)}`}>
                {getStatusIcon(stage.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{stage.name}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-muted-foreground">
                        {stage.records > 0 ? stage.records : '-'}
                      </span>
                      {stage.duration > 0 && (
                        <span className="text-xs text-muted-foreground">
                          {stage.duration}ms
                        </span>
                      )}
                    </div>
                  </div>
                  {stage.status === 'running' && (
                    <Progress value={stage.progress} className="mt-2 h-1" />
                  )}
                </div>
              </div>

              {/* Connecting line */}
              {index < stages.length - 1 && (
                <div className="flex justify-center my-1">
                  <ArrowRight className="h-3 w-3 text-muted-foreground" />
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-4 pt-3 border-t border-border">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Total Duration: {(totalDuration / 1000).toFixed(1)}s</span>
            <span>Throughput: {Math.round(totalRecords / (totalDuration / 1000))} records/sec</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}