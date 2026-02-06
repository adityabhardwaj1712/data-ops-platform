"use client"

import React from 'react'
import {
    Sparkles, FileText, Globe, Code, Network,
    FileSpreadsheet, Image, Activity, Lock
} from 'lucide-react'

export type ScrapeStrategy =
    | 'auto' | 'static' | 'browser' | 'api'
    | 'crawler' | 'document' | 'ocr' | 'streaming' | 'auth'

interface StrategyOption {
    value: ScrapeStrategy
    label: string
    description: string
    icon: React.ReactNode
    useCases: string[]
    badge?: string
}

const strategies: StrategyOption[] = [
    {
        value: 'auto',
        label: 'Auto-Detect',
        description: 'Automatically choose the best strategy',
        icon: <Sparkles className="w-5 h-5" />,
        useCases: ['General purpose', 'Unknown site structure'],
        badge: 'Recommended'
    },
    {
        value: 'static',
        label: 'Static HTML',
        description: 'Fast scraping for server-rendered pages',
        icon: <FileText className="w-5 h-5" />,
        useCases: ['Blogs', 'News sites', 'Simple catalogs'],
        badge: 'Fastest'
    },
    {
        value: 'browser',
        label: 'JavaScript Rendering',
        description: 'Full browser for React/Vue/Angular apps',
        icon: <Globe className="w-5 h-5" />,
        useCases: ['Modern SPAs', 'Infinite scroll', 'Dynamic content']
    },
    {
        value: 'api',
        label: 'API Scraping',
        description: 'Direct JSON endpoint access',
        icon: <Code className="w-5 h-5" />,
        useCases: ['Mobile apps', 'Fast data extraction', 'Structured APIs'],
        badge: '10x Faster'
    },
    {
        value: 'crawler',
        label: 'Multi-Page Crawler',
        description: 'Follow links and scrape entire sections',
        icon: <Network className="w-5 h-5" />,
        useCases: ['Product catalogs', 'Directory listings', 'Site archives']
    },
    {
        value: 'document',
        label: 'Document Extraction',
        description: 'Extract data from PDFs, Excel, CSV',
        icon: <FileSpreadsheet className="w-5 h-5" />,
        useCases: ['Financial reports', 'Government filings', 'Data tables']
    },
    {
        value: 'ocr',
        label: 'Image/OCR',
        description: 'Extract text from images and screenshots',
        icon: <Image className="w-5 h-5" />,
        useCases: ['Scanned documents', 'Charts', 'Receipts']
    },
    {
        value: 'streaming',
        label: 'Real-Time Monitoring',
        description: 'Continuous polling for live data',
        icon: <Activity className="w-5 h-5" />,
        useCases: ['Stock prices', 'Inventory tracking', 'Price alerts'],
        badge: 'Live'
    },
    {
        value: 'auth',
        label: 'Authenticated',
        description: 'Scrape behind login walls',
        icon: <Lock className="w-5 h-5" />,
        useCases: ['Private dashboards', 'Account data', 'Member areas'],
        badge: 'Advanced'
    }
]

interface StrategySelectorProps {
    selected: ScrapeStrategy
    onChange: (strategy: ScrapeStrategy) => void
}

export function StrategySelector({ selected, onChange }: StrategySelectorProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strategies.map((strategy) => (
                <div
                    key={strategy.value}
                    onClick={() => onChange(strategy.value)}
                    className={`
            relative p-5 rounded-xl border-2 cursor-pointer transition-all duration-300
            hover:shadow-lg hover:scale-[1.02]
            ${selected === strategy.value
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                            : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                        }
          `}
                >
                    {/* Badge */}
                    {strategy.badge && (
                        <div className="absolute top-3 right-3">
                            <span className="text-xs px-2 py-1 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold">
                                {strategy.badge}
                            </span>
                        </div>
                    )}

                    {/* Header */}
                    <div className="flex items-center gap-3 mb-3">
                        <div className={`
              p-2 rounded-lg
              ${selected === strategy.value
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                            }
            `}>
                            {strategy.icon}
                        </div>
                        <h3 className="font-semibold text-lg">{strategy.label}</h3>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 min-h-[40px]">
                        {strategy.description}
                    </p>

                    {/* Use Cases */}
                    <div className="flex flex-wrap gap-2">
                        {strategy.useCases.map((useCase) => (
                            <span
                                key={useCase}
                                className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-md text-gray-700 dark:text-gray-300"
                            >
                                {useCase}
                            </span>
                        ))}
                    </div>

                    {/* Selection Indicator */}
                    {selected === strategy.value && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-b-xl" />
                    )}
                </div>
            ))}
        </div>
    )
}
