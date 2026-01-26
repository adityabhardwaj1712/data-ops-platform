"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react'

interface DomainHealth {
  domain: string
  status: 'healthy' | 'warning' | 'error' | 'unknown'
  responseTime: number
  lastChecked: string
  successRate: number
}

export function SourceHealthCard() {
  const [domains, setDomains] = useState<DomainHealth[]>([
    { domain: 'linkedin.com', status: 'healthy', responseTime: 1200, lastChecked: '2m ago', successRate: 0.95 },
    { domain: 'indeed.com', status: 'warning', responseTime: 2500, lastChecked: '5m ago', successRate: 0.78 },
    { domain: 'glassdoor.com', status: 'healthy', responseTime: 1800, lastChecked: '1m ago', successRate: 0.92 },
    { domain: 'monster.com', status: 'error', responseTime: 0, lastChecked: '10m ago', successRate: 0.45 },
    { domain: 'dice.com', status: 'healthy', responseTime: 950, lastChecked: '30s ago', successRate: 0.98 },
    { domain: 'careerbuilder.com', status: 'warning', responseTime: 3200, lastChecked: '8m ago', successRate: 0.67 },
  ])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-3 w-3 text-green-500" />
      case 'warning':
        return <AlertTriangle className="h-3 w-3 text-yellow-500" />
      case 'error':
        return <XCircle className="h-3 w-3 text-red-500" />
      default:
        return <Clock className="h-3 w-3 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'warning':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'error':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const healthyCount = domains.filter(d => d.status === 'healthy').length
  const totalDomains = domains.length
  const overallHealth = (healthyCount / totalDomains) * 100

  return (
    <Card className="premium-card glow-border">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Source Health</CardTitle>
            <CardDescription>
              Domain availability and response times
            </CardDescription>
          </div>
          <Badge variant="outline" className={getStatusColor(overallHealth > 70 ? 'healthy' : overallHealth > 40 ? 'warning' : 'error')}>
            {overallHealth.toFixed(0)}% Healthy
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {domains.slice(0, 6).map((domain) => (
            <div key={domain.domain} className="flex items-center justify-between p-2 rounded-md bg-muted/50">
              <div className="flex items-center space-x-2">
                {getStatusIcon(domain.status)}
                <span className="text-sm font-medium">{domain.domain}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-muted-foreground">
                  {domain.responseTime > 0 ? `${domain.responseTime}ms` : 'N/A'}
                </span>
                <span className="text-xs text-muted-foreground">
                  {(domain.successRate * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Mini Heatmap */}
        <div className="mt-4 p-3 rounded-md bg-muted/30">
          <div className="text-xs text-muted-foreground mb-2">Response Time Heatmap</div>
          <div className="grid grid-cols-6 gap-1">
            {domains.map((domain, index) => (
              <div
                key={index}
                className={`h-3 rounded-sm ${
                  domain.responseTime < 1000 ? 'bg-green-500' :
                  domain.responseTime < 2000 ? 'bg-yellow-500' :
                  domain.responseTime < 3000 ? 'bg-orange-500' : 'bg-red-500'
                }`}
                title={`${domain.domain}: ${domain.responseTime}ms`}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}