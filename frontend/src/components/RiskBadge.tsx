import type { RiskSeverity, Priority } from '../types/demo_state'

const COLORS: Record<RiskSeverity | Priority, string> = {
  critical: 'bg-red-500/20 text-red-400 ring-1 ring-red-500/40',
  high:     'bg-orange-500/20 text-orange-400 ring-1 ring-orange-500/40',
  medium:   'bg-yellow-500/20 text-yellow-400 ring-1 ring-yellow-500/40',
  low:      'bg-green-500/20 text-green-400 ring-1 ring-green-500/40',
}

export default function RiskBadge({ level }: { level: RiskSeverity | Priority }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${COLORS[level]}`}>
      {level}
    </span>
  )
}
