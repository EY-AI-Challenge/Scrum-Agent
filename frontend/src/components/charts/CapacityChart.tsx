import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts'
import type { SprintPlanState } from '../../types/demo_state'

interface Props {
  sprints: SprintPlanState[]
}

export default function CapacityChart({ sprints }: Props) {
  const data = sprints.map((s) => ({
    name: s.sprint_id,
    planned: s.planned_points,
    capacity: s.capacity_points,
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: -8 }}>
        <XAxis dataKey="name" tick={{ fill: '#9CA3AF', fontSize: 11 }} />
        <YAxis tick={{ fill: '#9CA3AF', fontSize: 11 }} />
        <Tooltip
          contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 8 }}
          labelStyle={{ color: '#F3F4F6' }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: '#9CA3AF' }} />
        <Bar dataKey="capacity" fill="#374151" name="Capacity" radius={[4, 4, 0, 0]} />
        <Bar dataKey="planned" fill="#6366F1" name="Planned" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
