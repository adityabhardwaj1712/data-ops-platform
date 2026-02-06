"use client"

import React from 'react'

interface CrawlConfig {
    max_depth: number
    max_pages: number
    follow_external_links: boolean
    url_patterns?: string[]
}

interface CrawlerConfigPanelProps {
    config: CrawlConfig
    onChange: (config: CrawlConfig) => void
}

export function CrawlerConfigPanel({ config, onChange }: CrawlerConfigPanelProps) {
    return (
        <div className="space-y-6 p-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4">Crawler Configuration</h3>

            {/* Max Depth */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Max Depth
                    <span className="text-gray-500 ml-2 font-normal">
                        (How many levels deep to follow links)
                    </span>
                </label>
                <input
                    type="range"
                    value={config.max_depth}
                    onChange={(e) => onChange({ ...config, max_depth: parseInt(e.target.value) })}
                    min={1}
                    max={5}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-1">
                    <span>1 level</span>
                    <span className="font-semibold text-blue-600">{config.max_depth} levels</span>
                    <span>5 levels</span>
                </div>
            </div>

            {/* Max Pages */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Max Pages to Scrape
                </label>
                <input
                    type="number"
                    value={config.max_pages}
                    onChange={(e) => onChange({ ...config, max_pages: parseInt(e.target.value) || 1 })}
                    min={1}
                    max={500}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                />
                <p className="text-xs text-gray-500 mt-1">
                    Maximum number of pages to crawl (1-500)
                </p>
            </div>

            {/* Follow External Links */}
            <div className="flex items-center space-x-3">
                <input
                    type="checkbox"
                    id="follow-external"
                    checked={config.follow_external_links}
                    onChange={(e) => onChange({ ...config, follow_external_links: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="follow-external" className="text-sm font-medium cursor-pointer">
                    Follow external links (other domains)
                </label>
            </div>

            {/* URL Pattern Filter */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    URL Pattern Filter (regex)
                    <span className="text-gray-500 ml-2 font-normal">
                        (Optional)
                    </span>
                </label>
                <input
                    type="text"
                    placeholder="e.g., /product/.* or /category/.*"
                    value={config.url_patterns?.[0] || ''}
                    onChange={(e) => onChange({
                        ...config,
                        url_patterns: e.target.value ? [e.target.value] : undefined
                    })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 font-mono text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">
                    Only crawl URLs matching this pattern
                </p>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <p className="text-sm text-blue-800 dark:text-blue-300">
                    <strong>💡 Tip:</strong> Start with depth=2 and max_pages=20 for testing.
                    Crawling can take time depending on site structure.
                </p>
            </div>
        </div>
    )
}
