"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Database,
  Workflow,
  Eye,
  FileText,
  History,
  Settings,
  Zap,
  Moon,
  Sun
} from 'lucide-react'
import { useTheme } from 'next-themes'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Database,
    description: 'System pulse & health'
  },
  {
    name: 'Pipeline',
    href: '/pipeline',
    icon: Workflow,
    description: '6-layer data flow'
  },
  {
    name: 'Ghost Monitor',
    href: '/ghost',
    icon: Eye,
    description: 'Stealth operations'
  },
  {
    name: 'Intent Editor',
    href: '/intent',
    icon: FileText,
    description: 'Schema & extraction'
  },
  {
    name: 'Time Machine',
    href: '/timeline',
    icon: History,
    description: 'Version explorer'
  },
  {
    name: 'Jobs',
    href: '/jobs',
    icon: Zap,
    description: 'Task management'
  }
]

export function Navigation() {
  const pathname = usePathname()
  const { setTheme, theme } = useTheme()

  return (
    <nav className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Database className="h-4 w-4 text-primary" />
              </div>
              <div>
                <span className="text-lg font-bold">DataOps</span>
                <Badge variant="outline" className="ml-2 text-xs">
                  v2.0
                </Badge>
              </div>
            </Link>

            <div className="hidden md:flex items-center space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href

                return (
                  <Link key={item.name} href={item.href}>
                    <Button
                      variant={isActive ? "default" : "ghost"}
                      size="sm"
                      className={cn(
                        "h-9 px-3",
                        isActive && "bg-primary/10 text-primary hover:bg-primary/20"
                      )}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.name}
                    </Button>
                  </Link>
                )
              })}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="h-9 w-9 px-0"
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>

            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}