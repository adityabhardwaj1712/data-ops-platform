"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Download, FileText, FileSpreadsheet, Database, TrendingUp } from 'lucide-react'

interface ExportStat {
  format: 'excel' | 'csv' | 'json'
  count: number
  totalRecords: number
  lastExported: Date
  avgSize: string
}

export function ExportStatsCard() {
  const [stats] = useState({
    totalExports: 47,
    totalRecords: 12450,
    successRate: 0.98,
    avgProcessingTime: 8500
  })

  const [recentExports] = useState<ExportStat[]>([
    { format: 'excel', count: 23, totalRecords: 6540, lastExported: new Date(Date.now() - 1000 * 60 * 30), avgSize: '2.3MB' },
    { format: 'csv', count: 15, totalRecords: 4320, lastExported: new Date(Date.now() - 1000 * 60 * 60 * 2), avgSize: '1.8MB' },
    { format: 'json', count: 9, totalRecords: 1590, lastExported: new Date(Date.now() - 1000 * 60 * 60 * 6), avgSize: '956KB' }
  ])

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'excel':
        return <FileSpreadsheet className="h-4 w-4 text-green-500" />
      case 'csv':
        return <FileText className="h-4 w-4 text-blue-500" />
      case 'json':
        return <Database className="h-4 w-4 text-purple-500" />
      default:
        return <FileText className="h-4 w-4 text-gray-500" />
    }
  }

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / (1000 * 60))

    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ago`
  }

  return (
    <Card className="premium-card glow-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Export Stats</CardTitle>
            <CardDescription>
              Data delivery and downloads
            </CardDescription>
          </div>
          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
            {(stats.successRate * 100).toFixed(0)}% Success
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center p-3 rounded-md bg-muted/50">
            <div className="text-2xl font-bold">{stats.totalExports}</div>
            <div className="text-xs text-muted-foreground">Total Exports</div>
          </div>
          <div className="text-center p-3 rounded-md bg-muted/50">
            <div className="text-2xl font-bold">{formatNumber(stats.totalRecords)}</div>
            <div className="text-xs text-muted-foreground">Records Exported</div>
          </div>
        </div>

        {/* Export Formats */}
        <div className="space-y-3">
          {recentExports.map((exportStat) => (
            <div key={exportStat.format} className="flex items-center justify-between p-3 rounded-md bg-muted/30">
              <div className="flex items-center space-x-3">
                {getFormatIcon(exportStat.format)}
                <div>
                  <div className="text-sm font-medium capitalize">{exportStat.format}</div>
                  <div className="text-xs text-muted-foreground">
                    {exportStat.count} exports • {formatNumber(exportStat.totalRecords)} records
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">{exportStat.avgSize}</div>
                <div className="text-xs text-muted-foreground">
                  {formatTime(exportStat.lastExported)}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Performance Metrics */}
        <div className="mt-4 pt-3 border-t border-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Avg Processing Time</span>
            <span className="font-medium">{(stats.avgProcessingTime / 1000).toFixed(1)}s</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-muted-foreground">Throughput</span>
            <span className="font-medium flex items-center">
              <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
              {Math.round(stats.totalRecords / (stats.totalExports * stats.avgProcessingTime / 1000))} rec/sec
            </span>
          </div>
        </div>

        <div className="mt-4">
          <Button variant="outline" className="w-full" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Current Data
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}