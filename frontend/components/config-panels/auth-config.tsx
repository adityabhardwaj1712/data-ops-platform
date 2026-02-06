"use client"

import React from 'react'
import { AlertTriangle } from 'lucide-react'

type AuthMethod = 'cookies' | 'form_login' | 'api_token'

interface AuthConfig {
    method: AuthMethod
    credentials?: {
        username?: string
        password?: string
        token?: string
    }
    login_url?: string
    cookies?: Array<{ name: string; value: string; domain: string }>
}

interface AuthConfigPanelProps {
    config: AuthConfig
    onChange: (config: AuthConfig) => void
}

export function AuthConfigPanel({ config, onChange }: AuthConfigPanelProps) {
    return (
        <div className="space-y-6 p-6 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4">Authentication Configuration</h3>

            {/* Legal Warning */}
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-400 dark:border-yellow-700 rounded-lg p-4">
                <div className="flex gap-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="text-sm font-semibold text-yellow-800 dark:text-yellow-300 mb-1">
                            ⚠️ Legal Warning
                        </p>
                        <p className="text-sm text-yellow-700 dark:text-yellow-400">
                            Only scrape sites you have explicit permission to access.
                            Unauthorized access may violate Terms of Service and laws (CFAA, GDPR, etc.).
                        </p>
                    </div>
                </div>
            </div>

            {/* Authentication Method */}
            <div>
                <label className="block text-sm font-medium mb-2">
                    Authentication Method
                </label>
                <select
                    value={config.method}
                    onChange={(e) => onChange({ ...config, method: e.target.value as AuthMethod })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                >
                    <option value="cookies">Cookies (paste from browser)</option>
                    <option value="form_login">Form Login (username/password)</option>
                    <option value="api_token">API Token/Bearer</option>
                </select>
            </div>

            {/* Form Login Fields */}
            {config.method === 'form_login' && (
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Login URL
                        </label>
                        <input
                            type="url"
                            placeholder="https://example.com/login"
                            value={config.login_url || ''}
                            onChange={(e) => onChange({ ...config, login_url: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Username / Email
                        </label>
                        <input
                            type="text"
                            placeholder="your-username"
                            value={config.credentials?.username || ''}
                            onChange={(e) => onChange({
                                ...config,
                                credentials: { ...config.credentials, username: e.target.value }
                            })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={config.credentials?.password || ''}
                            onChange={(e) => onChange({
                                ...config,
                                credentials: { ...config.credentials, password: e.target.value }
                            })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            🔒 Credentials are encrypted and never logged
                        </p>
                    </div>
                </div>
            )}

            {/* Cookies */}
            {config.method === 'cookies' && (
                <div>
                    <label className="block text-sm font-medium mb-2">
                        Cookies JSON
                    </label>
                    <textarea
                        placeholder='[{"name": "session_id", "value": "abc123", "domain": ".example.com"}]'
                        rows={6}
                        value={config.cookies ? JSON.stringify(config.cookies, null, 2) : ''}
                        onChange={(e) => {
                            try {
                                const parsed = JSON.parse(e.target.value)
                                onChange({ ...config, cookies: parsed })
                            } catch {
                                // Invalid JSON, ignore
                            }
                        }}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                        Export cookies from browser DevTools (Application → Cookies)
                    </p>
                </div>
            )}

            {/* API Token */}
            {config.method === 'api_token' && (
                <div>
                    <label className="block text-sm font-medium mb-2">
                        API Token / Bearer Token
                    </label>
                    <input
                        type="password"
                        placeholder="sk_live_abc123..."
                        value={config.credentials?.token || ''}
                        onChange={(e) => onChange({
                            ...config,
                            credentials: { ...config.credentials, token: e.target.value }
                        })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                        Token will be sent as Authorization header
                    </p>
                </div>
            )}
        </div>
    )
}
