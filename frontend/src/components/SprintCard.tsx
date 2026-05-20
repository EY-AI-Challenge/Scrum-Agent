import type { SprintPlanState } from '../types/demo_state'

interface Props {
  sprint: SprintPlanState
}

export default function SprintCard({ sprint }: Props) {
  const pct = sprint.capacity_points > 0
    ? Math.round((sprint.planned_points / sprint.capacity_points) * 100)
    : 0
  const isOverloaded = pct > 100

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-gray-400">{sprint.sprint_id}</span>
        <span className="text-xs text-gray-500">W{sprint.start_week}–W{sprint.end_week}</span>
      </div>

      <p className="text-sm text-gray-300 font-medium leading-snug">{sprint.goal}</p>
      <p className="text-xs text-gray-500 line-clamp-2">{sprint.focus}</p>

      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">{sprint.planned_points} / {sprint.capacity_points} pts</span>
          <span className={isOverloaded ? 'text-red-400 font-medium' : 'text-gray-400'}>{pct}%</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${isOverloaded ? 'bg-red-500' : 'bg-indigo-500'}`}
            style={{ width: `${Math.min(pct, 100)}%` }}
          />
        </div>
      </div>

      <div className="text-xs text-gray-500">{sprint.item_ids.length} items</div>
    </div>
  )
}
