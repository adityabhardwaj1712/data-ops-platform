"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Database,
  Eye,
  Sparkles,
  Brain,
  Shield,
  Archive,
  ArrowRight,
  Play,
  Pause,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

interface PipelineNode {
  id: string
  name: string
  description: string
  icon: React.ComponentType<any>
  status: 'idle' | 'running' | 'completed' | 'warning' | 'error'
  progress: number
  records: number
  processingTime: number
  efficiency: number
}

export default function PipelinePage() {
  const [nodes] = useState<PipelineNode[]>([
    {
      id: 'source',
      name: 'Source Intelligence',
      description: 'URL discovery & validation',
      icon: Database,
      status: 'completed',
      progress: 100,
      records: 450,
      processingTime: 1200,
      efficiency: 0.95
    },
    {
      id: 'fetch',
      name: 'Invisible Fetching',
      description: 'Stealth page acquisition',
      icon: Eye,
      status: 'completed',
      progress: 100,
      records: 445,
      processingTime: 8500,
      efficiency: 0.87
    },
    {
      id: 'clean',
      name: 'Content Cleaning',
      description: 'Noise reduction & parsing',
      icon: Sparkles,
      status: 'completed',
      progress: 100,
      records: 445,
      processingTime: 3200,
      efficiency: 0.92
    },
    {
      id: 'extract',
      name: 'Intent Extraction',
      description: 'AI-powered data extraction',
      icon: Brain,
      status: 'running',
      progress: 75,
      records: 334,
      processingTime: 0,
      efficiency: 0.89
    },
    {
      id: 'quality',
      name: 'Quality Assurance',
      description: 'Validation & deduplication',
      icon: Shield,
      status: 'idle',
      progress: 0,
      records: 0,
      processingTime: 0,
      efficiency: 0.94
    },
    {
      id: 'version',
      name: 'Version Storage',
      description: 'Immutable dataset versioning',
      icon: Archive,
      status: 'idle',
      progress: 0,
      records: 0,
      processingTime: 0,
      efficiency: 0.98
    }
  ])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-500/50 bg-green-500/10'
      case 'running':
        return 'border-blue-500/50 bg-blue-500/10 glow-border'
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/10 animate-pulse'
      case 'error':
        return 'border-red-500/50 bg-red-500/10'
      default:
        return 'border-gray-500/50 bg-gray-500/10'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running':
        return <Play className="h-4 w-4 text-blue-500" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return <Pause className="h-4 w-4 text-gray-500" />
    }
  }

  const getConnectorColor = (fromStatus: string, toStatus: string) => {
    if (fromStatus === 'completed' && toStatus === 'running') {
      return 'border-blue-500/60'
    }
    if (fromStatus === 'completed' && toStatus === 'completed') {
      return 'border-green-500/60'
    }
    return 'border-gray-500/30'
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Pipeline Flow</h1>
          <p className="text-muted-foreground mt-2">
            Real-time visualization of your 6-layer data processing pipeline
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
            1 Job Running
          </Badge>
          <Button>
            <Play className="h-4 w-4 mr-2" />
            Start New Job
          </Button>
        </div>
      </div>

      {/* Pipeline Visualization */}
      <Card className="premium-card">
        <CardHeader>
          <CardTitle>Data Processing Pipeline</CardTitle>
          <CardDescription>
            Watch data flow through each layer in real-time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {/* Pipeline Nodes */}
            <div className="flex items-center justify-between min-h-[400px] px-8">
              {nodes.map((node, index) => {
                const Icon = node.icon
                const nextNode = nodes[index + 1]

                return (
                  <div key={node.id} className="flex items-center">
                    {/* Node */}
                    <div className={`relative p-6 rounded-xl border-2 transition-all duration-500 ${getStatusColor(node.status)}`}>
                      <div className="text-center">
                        <div className="flex items-center justify-center mb-3">
                          <div className={`p-3 rounded-full ${node.status === 'running' ? 'bg-blue-500/20' : 'bg-muted/50'}`}>
                            <Icon className="h-6 w-6" />
                          </div>
                        </div>
                        <h3 className="font-semibold text-sm mb-1">{node.name}</h3>
                        <p className="text-xs text-muted-foreground mb-3">{node.description}</p>

                        <div className="space-y-2">
                          <div className="flex items-center justify-center space-x-1">
                            {getStatusIcon(node.status)}
                            <span className="text-xs capitalize">{node.status}</span>
                          </div>

                          {node.records > 0 && (
                            <div className="text-xs text-muted-foreground">
                              {node.records} records
                            </div>
                          )}

                          {node.processingTime > 0 && (
                            <div className="text-xs text-muted-foreground">
                              {(node.processingTime / 1000).toFixed(1)}s
                            </div>
                          )}

                          {node.status === 'running' && (
                            <Progress value={node.progress} className="w-16 h-1 mx-auto" />
                          )}
                        </div>
                      </div>

                      {/* Efficiency indicator */}
                      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                        <Badge variant="outline" className="text-xs bg-background/80">
                          {(node.efficiency * 100).toFixed(0)}% eff
                        </Badge>
                      </div>
                    </div>

                    {/* Connector */}
                    {index < nodes.length - 1 && (
                      <div className="flex items-center mx-4">
                        <div className={`w-16 h-0.5 ${getConnectorColor(node.status, nextNode?.status || 'idle')} transition-colors duration-1000`} />
                        <ArrowRight className={`h-4 w-4 ${node.status === 'completed' && nextNode?.status === 'running' ? 'text-blue-500 animate-pulse' : 'text-muted-foreground'}`} />
                        <div className={`w-16 h-0.5 ${getConnectorColor(node.status, nextNode?.status || 'idle')} transition-colors duration-1000`} />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Pipeline Stats */}
            <div className="mt-8 grid grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-md bg-muted/30">
                <div className="text-2xl font-bold">6</div>
                <div className="text-xs text-muted-foreground">Layers Active</div>
              </div>
              <div className="text-center p-4 rounded-md bg-muted/30">
                <div className="text-2xl font-bold">334</div>
                <div className="text-xs text-muted-foreground">Records Processed</div>
              </div>
              <div className="text-center p-4 rounded-md bg-muted/30">
                <div className="text-2xl font-bold">13.1s</div>
                <div className="text-xs text-muted-foreground">Total Processing Time</div>
              </div>
              <div className="text-center p-4 rounded-md bg-muted/30">
                <div className="text-2xl font-bold">25.5</div>
                <div className="text-xs text-muted-foreground">Records/Second</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Layer Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {nodes.map((node) => (
          <Card key={node.id} className="premium-card">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <node.icon className="h-5 w-5" />
                <CardTitle className="text-base">{node.name}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge variant="outline" className={getStatusColor(node.status)}>
                    {node.status}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Records:</span>
                  <span>{node.records || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Efficiency:</span>
                  <span>{(node.efficiency * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Processing Time:</span>
                  <span>{node.processingTime ? `${(node.processingTime / 1000).toFixed(1)}s` : '-'}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}