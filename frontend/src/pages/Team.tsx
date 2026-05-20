import { useDemoStore } from '../store/demoState'
import type { TeamMemberState, AllocationState } from '../types/demo_state'

export default function Team() {
  const state = useDemoStore((s) => s.state)
  if (!state) return null

  const overCapacityMembers = new Set(
    state.allocations.filter((a) => a.over_capacity).map((a) => a.member_id)
  )

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">Team</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {state.team_members.map((member) => {
          const memberAllocations = state.allocations.filter((a) => a.member_id === member.member_id)
          const totalPoints = memberAllocations.reduce((s, a) => s + a.assigned_points, 0)
          const isOver = overCapacityMembers.has(member.member_id)

          return (
            <MemberCard
              key={member.member_id}
              member={member}
              allocations={memberAllocations}
              totalPoints={totalPoints}
              isOver={isOver}
            />
          )
        })}
      </div>
    </div>
  )
}

function MemberCard({
  member,
  allocations,
  totalPoints,
  isOver,
}: {
  member: TeamMemberState
  allocations: AllocationState[]
  totalPoints: number
  isOver: boolean
}) {
  const capPct = Math.round((totalPoints / (member.capacity_per_sprint * 4)) * 100)

  return (
    <div className={`bg-gray-900 border rounded-xl p-4 space-y-3 ${isOver ? 'border-red-700' : 'border-gray-800'}`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-white text-sm">{member.name}</p>
          <p className="text-xs text-gray-400">{member.role}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="text-xs text-gray-500">{member.experience_years}y exp</span>
          {isOver && <span className="text-xs text-red-400 font-medium">Over capacity</span>}
        </div>
      </div>

      {/* Capacity bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{totalPoints} pts assigned</span>
          <span>{member.capacity_per_sprint * 4} total cap.</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${isOver ? 'bg-red-500' : 'bg-indigo-500'}`}
            style={{ width: `${Math.min(capPct, 100)}%` }}
          />
        </div>
      </div>

      {/* Skills */}
      <div className="flex flex-wrap gap-1">
        {member.skills.slice(0, 5).map((skill) => (
          <span key={skill} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">
            {skill}
          </span>
        ))}
        {member.skills.length > 5 && (
          <span className="text-xs text-gray-600">+{member.skills.length - 5}</span>
        )}
      </div>

      {/* Allocations summary */}
      {allocations.length > 0 && (
        <div className="space-y-1 pt-1 border-t border-gray-800">
          {allocations.slice(0, 3).map((a) => (
            <div key={a.allocation_id} className="flex justify-between text-xs">
              <span className="text-gray-400 truncate mr-2">{a.item_id}</span>
              <span className="text-gray-500 flex-shrink-0">{a.assigned_points}pts</span>
            </div>
          ))}
          {allocations.length > 3 && (
            <p className="text-xs text-gray-600">+{allocations.length - 3} more</p>
          )}
        </div>
      )}
    </div>
  )
}
