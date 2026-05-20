import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import type { BacklogItemState, Priority } from '../../types/demo_state'

const COLORS: Record<Priority, string> = {
  critical: '#EF4444',
  high:     '#F97316',
  medium:   '#EAB308',
  low:      '#22C55E',
}

interface Props {
  items: BacklogItemState[]
}

export default function PriorityChart({ items }: Props) {
  const counts = items.reduce<Record<string, number>>((acc, item) => {
    acc[item.priority] = (acc[item.priority] ?? 0) + 1
    return acc
  }, {})

  const data = (Object.keys(COLORS) as Priority[])
    .filter((p) => counts[p])
    .map((p) => ({ name: p, value: counts[p] }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={70}
          label={({ name, value }) => `${name} (${value})`}
          labelLine={{ stroke: '#6B7280' }}
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name as Priority]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 8 }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
