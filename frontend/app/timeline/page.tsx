"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  History,
  Clock,
  Download,
  Eye,
  ArrowRight,
  Plus,
  Minus,
  RotateCcw,
  TrendingUp,
  TrendingDown
} from 'lucide-react'

interface DatasetVersion {
  id: string
  version: number
  timestamp: Date
  recordCount: number
  changeSummary: {
    added: number
    removed: number
    modified: number
  }
  snapshot: any[]
}

interface DiffItem {
  field: string
  oldValue: any
  newValue: any
  type: 'added' | 'removed' | 'modified'
}

export default function TimelinePage() {
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null)
  const [compareVersions, setCompareVersions] = useState<{from: number | null, to: number | null}>({
    from: null,
    to: null
  })
  const [diffData, setDiffData] = useState<DiffItem[]>([])

  // Mock dataset versions
  const versions: DatasetVersion[] = [
    {
      id: 'v5',
      version: 5,
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
      recordCount: 342,
      changeSummary: { added: 12, removed: 3, modified: 8 },
      snapshot: []
    },
    {
      id: 'v4',
      version: 4,
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      recordCount: 333,
      changeSummary: { added: 25, removed: 5, modified: 15 },
      snapshot: []
    },
    {
      id: 'v3',
      version: 3,
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6), // 6 hours ago
      recordCount: 313,
      changeSummary: { added: 45, removed: 8, modified: 22 },
      snapshot: []
    },
    {
      id: 'v2',
      version: 2,
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
      recordCount: 276,
      changeSummary: { added: 89, removed: 12, modified: 34 },
      snapshot: []
    },
    {
      id: 'v1',
      version: 1,
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
      recordCount: 199,
      changeSummary: { added: 199, removed: 0, modified: 0 },
      snapshot: []
    }
  ]

  // Mock diff data
  const mockDiffData: DiffItem[] = [
    { field: 'salary', oldValue: '$100,000 - $130,000', newValue: '$110,000 - $140,000', type: 'modified' },
    { field: 'company', oldValue: null, newValue: 'NewTech Solutions', type: 'added' },
    { field: 'location', oldValue: 'Remote', newValue: 'San Francisco, CA', type: 'modified' },
    { field: 'experience_level', oldValue: 'Mid-level', newValue: null, type: 'removed' },
    { field: 'job_type', oldValue: null, newValue: 'Full-time', type: 'added' }
  ]

  const handleVersionSelect = (version: number) => {
    setSelectedVersion(version)
  }

  const handleCompareSelect = (version: number, type: 'from' | 'to') => {
    setCompareVersions(prev => ({
      ...prev,
      [type]: version
    }))

    if (type === 'to' && compareVersions.from) {
      // Generate mock diff data
      setDiffData(mockDiffData)
    }
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    const minutes = Math.floor(diff / (1000 * 60))
    return `${minutes}m ago`
  }

  const getChangeColor = (count: number) => {
    if (count === 0) return 'text-gray-400'
    if (count < 10) return 'text-green-400'
    if (count < 25) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Time Machine</h1>
          <p className="text-muted-foreground mt-2">
            Explore dataset evolution through time with version diffs and change tracking
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Version
          </Button>
          <Button>
            <RotateCcw className="h-4 w-4 mr-2" />
            Restore Version
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Sidebar */}
        <Card className="premium-card lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <History className="h-5 w-5 mr-2" />
              Dataset Timeline
            </CardTitle>
            <CardDescription>
              Version history with change summaries
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-96">
              <div className="space-y-1 p-6">
                {versions.map((version, index) => (
                  <div
                    key={version.id}
                    className={`relative p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedVersion === version.version
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50'
                    }`}
                    onClick={() => handleVersionSelect(version.version)}
                  >
                    {/* Timeline line */}
                    {index < versions.length - 1 && (
                      <div className="absolute left-6 top-12 w-0.5 h-8 bg-border" />
                    )}

                    {/* Version dot */}
                    <div className="absolute left-4 top-6 w-4 h-4 rounded-full bg-primary border-2 border-background" />

                    <div className="ml-8">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">Version {version.version}</span>
                        <Badge variant="outline" className="text-xs">
                          {version.recordCount} records
                        </Badge>
                      </div>

                      <div className="text-sm text-muted-foreground mb-2">
                        {formatTime(version.timestamp)}
                      </div>

                      <div className="flex items-center space-x-4 text-xs">
                        <div className={`flex items-center ${getChangeColor(version.changeSummary.added)}`}>
                          <Plus className="h-3 w-3 mr-1" />
                          {version.changeSummary.added}
                        </div>
                        <div className={`flex items-center ${getChangeColor(version.changeSummary.removed)}`}>
                          <Minus className="h-3 w-3 mr-1" />
                          {version.changeSummary.removed}
                        </div>
                        <div className={`flex items-center ${getChangeColor(version.changeSummary.modified)}`}>
                          <ArrowRight className="h-3 w-3 mr-1" />
                          {version.changeSummary.modified}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Version Comparison Controls */}
          <Card className="premium-card">
            <CardHeader>
              <CardTitle className="text-lg">Version Comparison</CardTitle>
              <CardDescription>
                Compare any two versions to see what changed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <label className="text-sm font-medium mb-2 block">From Version</label>
                  <select
                    className="w-full p-2 rounded-md border border-input bg-background"
                    value={compareVersions.from || ''}
                    onChange={(e) => handleCompareSelect(Number(e.target.value), 'from')}
                  >
                    <option value="">Select version...</option>
                    {versions.map(v => (
                      <option key={v.id} value={v.version}>Version {v.version}</option>
                    ))}
                  </select>
                </div>

                <ArrowRight className="h-5 w-5 text-muted-foreground mt-6" />

                <div className="flex-1">
                  <label className="text-sm font-medium mb-2 block">To Version</label>
                  <select
                    className="w-full p-2 rounded-md border border-input bg-background"
                    value={compareVersions.to || ''}
                    onChange={(e) => handleCompareSelect(Number(e.target.value), 'to')}
                  >
                    <option value="">Select version...</option>
                    {versions.map(v => (
                      <option key={v.id} value={v.version}>Version {v.version}</option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Diff View */}
          {diffData.length > 0 && (
            <Card className="premium-card">
              <CardHeader>
                <CardTitle className="text-lg">Change Details</CardTitle>
                <CardDescription>
                  Field-level changes between versions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {diffData.map((diff, index) => (
                    <div key={index} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <span className="font-medium capitalize">{diff.field.replace(/_/g, ' ')}</span>
                        <Badge variant="outline" className={
                          diff.type === 'added' ? 'border-green-500/50 text-green-400' :
                          diff.type === 'removed' ? 'border-red-500/50 text-red-400' :
                          'border-yellow-500/50 text-yellow-400'
                        }>
                          {diff.type}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-muted-foreground mb-1">Before</div>
                          <div className="text-sm p-2 bg-red-500/10 border border-red-500/20 rounded min-h-[2rem] flex items-center">
                            {diff.oldValue !== null ? String(diff.oldValue) : <span className="text-muted-foreground italic">null</span>}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-muted-foreground mb-1">After</div>
                          <div className="text-sm p-2 bg-green-500/10 border border-green-500/20 rounded min-h-[2rem] flex items-center">
                            {diff.newValue !== null ? String(diff.newValue) : <span className="text-muted-foreground italic">null</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Version Details */}
          {selectedVersion && (
            <Card className="premium-card">
              <CardHeader>
                <CardTitle className="text-lg">Version {selectedVersion} Details</CardTitle>
                <CardDescription>
                  Snapshot information and statistics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 rounded-md bg-muted/30">
                    <div className="text-2xl font-bold">
                      {versions.find(v => v.version === selectedVersion)?.recordCount}
                    </div>
                    <div className="text-xs text-muted-foreground">Total Records</div>
                  </div>
                  <div className="text-center p-4 rounded-md bg-green-500/10">
                    <div className="text-2xl font-bold text-green-400">
                      +{versions.find(v => v.version === selectedVersion)?.changeSummary.added}
                    </div>
                    <div className="text-xs text-muted-foreground">Added</div>
                  </div>
                  <div className="text-center p-4 rounded-md bg-red-500/10">
                    <div className="text-2xl font-bold text-red-400">
                      -{versions.find(v => v.version === selectedVersion)?.changeSummary.removed}
                    </div>
                    <div className="text-xs text-muted-foreground">Removed</div>
                  </div>
                  <div className="text-center p-4 rounded-md bg-yellow-500/10">
                    <div className="text-2xl font-bold text-yellow-400">
                      {versions.find(v => v.version === selectedVersion)?.changeSummary.modified}
                    </div>
                    <div className="text-xs text-muted-foreground">Modified</div>
                  </div>
                </div>

                <div className="mt-6">
                  <Button className="w-full">
                    <Eye className="h-4 w-4 mr-2" />
                    View Full Dataset
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}