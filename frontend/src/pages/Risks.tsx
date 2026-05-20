import { useState, useMemo } from 'react'
import { useDemoStore } from '../store/demoState'
import RiskBadge from '../components/RiskBadge'
import type { RiskSeverity, RiskCategory } from '../types/demo_state'

export default function Risks() {
  const state = useDemoStore((s) => s.state)
  const [severityFilter, setSeverityFilter] = useState<RiskSeverity | ''>('')
  const [categoryFilter, setCategoryFilter] = useState<RiskCategory | ''>('')

  const risks = useMemo(() => {
    if (!state) return []
    return state.risks.filter((r) => {
      if (severityFilter && r.severity !== severityFilter) return false
      if (categoryFilter && r.category !== categoryFilter) return false
      return true
    }).sort((a, b) => {
      const order: RiskSeverity[] = ['critical', 'high', 'medium', 'low']
      return order.indexOf(a.severity) - order.indexOf(b.severity)
    })
  }, [state, severityFilter, categoryFilter])

  if (!state) return null

  return (
    <div className="p-6 space-y-5">
      <h2 className="text-2xl font-bold text-white">Risk Register</h2>

      {/* Filters */}
      <div className="flex gap-3">
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value as RiskSeverity | '')}
          className="bg-gray-800 text-sm text-gray-200 rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All severities</option>
          {(['critical', 'high', 'medium', 'low'] as RiskSeverity[]).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value as RiskCategory | '')}
          className="bg-gray-800 text-sm text-gray-200 rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All categories</option>
          {(['planning','compliance','data','security','capacity','dependency'] as RiskCategory[]).map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <span className="ml-auto text-xs text-gray-500 self-center">{risks.length} risks</span>
      </div>

      <div className="space-y-3">
        {risks.map((risk) => (
          <div key={risk.risk_id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <RiskBadge level={risk.severity} />
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">{risk.category}</span>
                {risk.project_id && (
                  <span className="text-xs text-gray-500">{risk.project_id}</span>
                )}
              </div>
              <span className="text-xs font-mono text-gray-600">{risk.risk_id}</span>
            </div>

            <h4 className="text-sm font-semibold text-white">{risk.title}</h4>
            <p className="text-sm text-gray-400 leading-relaxed">{risk.description}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 border-t border-gray-800">
              <div>
                <p className="text-xs text-gray-500 mb-1">Mitigation</p>
                <p className="text-xs text-gray-300">{risk.mitigation}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Owner suggestion</p>
                <p className="text-xs text-gray-300">{risk.owner_suggestion}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
