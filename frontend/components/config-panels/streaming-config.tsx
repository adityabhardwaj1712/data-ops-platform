"use client"

import React from 'react'

interface StreamingConfig {
    poll_interval_seconds: number
    max_duration_minutes: number
    change_threshold: number
    webhook_url?: string
}

interface StreamingConfigPanelProps {
    config: StreamingConfig
    onChange: (config: StreamingConfig) => void
}

export function StreamingConfigPanel({ config, onChange }: StreamingConfigPanelProps) {
    return (
        <div className="space-y-6 p-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4">Real-Time Monitoring Configuration</h3>

            {/* Poll Interval */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Poll Interval
                    <span className="text-gray-500 ml-2 font-normal">
                        (How often to check for changes)
                    </span>
                </label>
                <div className="flex items-center gap-4">
                    <input
                        type="range"
                        value={config.poll_interval_seconds}
                        onChange={(e) => onChange({ ...config, poll_interval_seconds: parseInt(e.target.value) })}
                        min={10}
                        max={3600}
                        step={10}
                        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                    />
                    <span className="text-sm font-semibold text-blue-600 min-w-[80px]">
                        {config.poll_interval_seconds}s
                    </span>
                </div>
                <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mt-1">
                    <span>10s (Fast)</span>
                    <span>1 hour (Slow)</span>
                </div>
            </div>

            {/* Max Duration */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Max Monitoring Duration (minutes)
                </label>
                <input
                    type="number"
                    value={config.max_duration_minutes}
                    onChange={(e) => onChange({ ...config, max_duration_minutes: parseInt(e.target.value) || 1 })}
                    min={1}
                    max={1440}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                />
                <p className="text-xs text-gray-500 mt-1">
                    How long to monitor before auto-stopping (1-1440 minutes / 24 hours)
                </p>
            </div>

            {/* Change Threshold */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Change Threshold (%)
                    <span className="text-gray-500 ml-2 font-normal">
                        (Alert when data changes by this amount)
                    </span>
                </label>
                <div className="flex items-center gap-4">
                    <input
                        type="range"
                        value={config.change_threshold * 100}
                        onChange={(e) => onChange({ ...config, change_threshold: parseFloat(e.target.value) / 100 })}
                        min={0}
                        max={100}
                        step={1}
                        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                    />
                    <span className="text-sm font-semibold text-blue-600 min-w-[60px]">
                        {(config.change_threshold * 100).toFixed(0)}%
                    </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                    Alert triggers when {(config.change_threshold * 100).toFixed(0)}% or more fields change
                </p>
            </div>

            {/* Webhook URL */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Webhook URL (Optional)
                    <span className="text-gray-500 ml-2 font-normal">
                        (Receive alerts via HTTP POST)
                    </span>
                </label>
                <input
                    type="url"
                    placeholder="https://your-server.com/webhook"
                    value={config.webhook_url || ''}
                    onChange={(e) => onChange({ ...config, webhook_url: e.target.value || undefined })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                />
                <p className="text-xs text-gray-500 mt-1">
                    Webhook will receive JSON payload with old/new data on changes
                </p>
            </div>

            {/* Info Box */}
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <p className="text-sm text-green-800 dark:text-green-300">
                    <strong>📊 Use Cases:</strong> Monitor stock prices, track inventory changes,
                    get alerts on price drops, or watch for new listings.
                </p>
            </div>

            {/* Estimated Stats */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                        {Math.floor(config.max_duration_minutes * 60 / config.poll_interval_seconds)}
                    </p>
                    <p className="text-xs text-gray-500">Total Checks</p>
                </div>
                <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                        ~{Math.ceil(config.max_duration_minutes / 60)}h
                    </p>
                    <p className="text-xs text-gray-500">Duration</p>
                </div>
            </div>
        </div>
    )
}
