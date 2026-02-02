"use client"

import { useState } from "react"
import { Search, Check, AlertCircle, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

export function SelectorTester() {
    const [url, setUrl] = useState("https://flipkart.com/product/12345")
    const [selector, setSelector] = useState(".price-tag")
    const [result, setResult] = useState<null | any>(null)
    const [loading, setLoading] = useState(false)

    const handleTest = async () => {
        setLoading(true)
        // Simulate API call
        setTimeout(() => {
            setResult({
                matched: true,
                count: 1,
                sample: "₹29,999",
                confidence: 0.95
            })
            setLoading(false)
        }, 1500)
    }

    return (
        <div className="glass-card h-full">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold font-outfit flex items-center gap-2">
                    <Search className="h-5 w-5 text-purple-400" />
                    Selector Tester
                </h3>
                <Badge variant="outline" className="text-[10px] uppercase tracking-wider bg-white/5">
                    Dev Tool
                </Badge>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="text-xs text-muted-foreground font-bold uppercase tracking-wider mb-2 block">
                        Target URL
                    </label>
                    <Input
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="bg-black/20 border-white/10 text-xs font-mono"
                    />
                </div>

                <div>
                    <label className="text-xs text-muted-foreground font-bold uppercase tracking-wider mb-2 block">
                        CSS Selector
                    </label>
                    <div className="flex gap-2">
                        <Input
                            value={selector}
                            onChange={(e) => setSelector(e.target.value)}
                            className="bg-black/20 border-white/10 text-xs font-mono"
                        />
                        <Button
                            size="sm"
                            className="bg-primary hover:bg-primary/90"
                            onClick={handleTest}
                            disabled={loading}
                        >
                            {loading ? "..." : <ArrowRight className="h-4 w-4" />}
                        </Button>
                    </div>
                </div>

                {result && (
                    <div className="mt-6 p-4 rounded-xl bg-green-500/10 border border-green-500/20 animate-in">
                        <div className="flex items-center gap-2 mb-2 text-green-400">
                            <Check className="h-4 w-4" />
                            <span className="font-bold text-sm">Match Found</span>
                        </div>
                        <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Count:</span>
                                <span className="text-white font-mono">{result.count}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Sample:</span>
                                <span className="text-white font-mono bg-black/40 px-2 py-0.5 rounded">{result.sample}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
