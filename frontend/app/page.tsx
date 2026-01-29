"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Globe, List } from 'lucide-react'
import Link from 'next/link'

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">DataOps Scraper</h1>
        <p className="text-muted-foreground mt-2">
          Reliable, human-verified scraping system.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link href="/scrape">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Globe className="mr-2 h-5 w-5 text-primary" />
                New Scrape
              </CardTitle>
              <CardDescription>Start a new scraping job (Single, List, Config)</CardDescription>
            </CardHeader>
          </Card>
        </Link>

        <Link href="/jobs">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center">
                <List className="mr-2 h-5 w-5 text-blue-500" />
                Job Status
              </CardTitle>
              <CardDescription>View running and completed jobs</CardDescription>
            </CardHeader>
          </Card>
        </Link>
      </div>
    </div>
  )
}