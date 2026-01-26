"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface QualityMetrics {
  overall: number
  fieldLevel: number
  deduplication: number
  schema: number
  humanReview: number
}

export function QualityScoreGauge() {
  const [metrics, setMetrics] = useState<QualityMetrics>({
    overall: 0.87,
    fieldLevel: 0.84,
    deduplication: 0.92,
    schema: 0.95,
    humanReview: 0.78
  })

  const [trend, setTrend] = useState<'up' | 'down' | 'stable'>('up')

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        overall: Math.max(0.7, Math.min(0.98, prev.overall + (Math.random() - 0.5) * 0.02))
      }))
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  const radius = 60
  const circumference = 2 * Math.PI * radius
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (metrics.overall * circumference)

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return '#10b981' // green
    if (score >= 0.8) return '#f59e0b' // yellow
    if (score >= 0.7) return '#f97316' // orange
    return '#ef4444' // red
  }

  const getScoreLabel = (score: number) => {
    if (score >= 0.9) return 'Excellent'
    if (score >= 0.8) return 'Good'
    if (score >= 0.7) return 'Fair'
    return 'Needs Attention'
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-3 w-3 text-green-500" />
      case 'down':
        return <TrendingDown className="h-3 w-3 text-red-500" />
      default:
        return <Minus className="h-3 w-3 text-gray-500" />
    }
  }

  return (
    <Card className="premium-card glow-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Quality Score</CardTitle>
            <CardDescription>
              Aggregate trust score of dataset
            </CardDescription>
          </div>
          <Badge variant="outline" className="flex items-center space-x-1">
            {getTrendIcon()}
            <span>{getScoreLabel(metrics.overall)}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Circular Gauge */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <svg width="140" height="140" className="transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="70"
                cy="70"
                r={radius}
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-muted"
              />
              {/* Progress circle */}
              <circle
                cx="70"
                cy="70"
                r={radius}
                stroke={getScoreColor(metrics.overall)}
                strokeWidth="8"
                fill="transparent"
                strokeDasharray={strokeDasharray}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-in-out"
              />
            </svg>
            {/* Center text */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {(metrics.overall * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-muted-foreground">Trust Score</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quality Metrics */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Field-Level Confidence</span>
            <span className="font-medium">{(metrics.fieldLevel * 100).toFixed(0)}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Deduplication Rate</span>
            <span className="font-medium">{(metrics.deduplication * 100).toFixed(0)}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Schema Validation</span>
            <span className="font-medium">{(metrics.schema * 100).toFixed(0)}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Human Review Rate</span>
            <span className="font-medium">{(metrics.humanReview * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* Mini trend chart */}
        <div className="mt-4 p-3 rounded-md bg-muted/30">
          <div className="text-xs text-muted-foreground mb-2">Quality Trend (24h)</div>
          <div className="flex items-end space-x-1 h-8">
            {[0.82, 0.85, 0.83, 0.87, 0.89, 0.86, 0.88, 0.87].map((value, index) => (
              <div
                key={index}
                className="bg-primary/60 rounded-sm flex-1"
                style={{ height: `${value * 100}%` }}
                title={`${(value * 100).toFixed(0)}%`}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}