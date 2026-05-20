import type { ProjectState, BacklogItemState, AllocationState } from '../types/demo_state'
import DomainBadge from './DomainBadge'

interface Props {
  project: ProjectState
  backlogItems: BacklogItemState[]
  allocations: AllocationState[]
}

export default function ProjectCard({ project, backlogItems, allocations }: Props) {
  const total = backlogItems.length
  const done = backlogItems.filter((i) => i.status === 'done').length
  const inProgress = backlogItems.filter((i) => i.status === 'in_progress').length
  const overCapacity = allocations.filter((a) => a.over_capacity).length
  const pct = total > 0 ? Math.round((done / total) * 100) : 0

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-white text-sm">{project.name}</h3>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{project.summary}</p>
        </div>
        <DomainBadge domain={project.domain} />
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{done}/{total} items done</span>
          <span>{pct}%</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${pct}%` }} />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <Stat label="MVP" value={`W${project.mvp_week}`} />
        <Stat label="In Progress" value={String(inProgress)} />
        <Stat
          label="Over Cap."
          value={String(overCapacity)}
          highlight={overCapacity > 0}
        />
      </div>
    </div>
  )
}

function Stat({ label, value, highlight = false }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="bg-gray-800/60 rounded-lg py-2 px-1">
      <div className={`text-base font-bold ${highlight ? 'text-red-400' : 'text-white'}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  )
}
