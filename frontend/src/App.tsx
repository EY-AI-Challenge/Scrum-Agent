import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import Dashboard from './pages/Dashboard'
import Backlog from './pages/Backlog'
import Sprints from './pages/Sprints'
import Team from './pages/Team'
import Risks from './pages/Risks'
import Agent from './pages/Agent'
import Chat from './pages/Chat'
import { useDemoStore } from './store/demoState'

export default function App() {
  const load = useDemoStore((s) => s.load)
  useEffect(() => { load() }, [load])

  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="backlog" element={<Backlog />} />
        <Route path="sprints" element={<Sprints />} />
        <Route path="team" element={<Team />} />
        <Route path="risks" element={<Risks />} />
        <Route path="agent" element={<Agent />} />
        <Route path="chat" element={<Chat />} />
      </Route>
    </Routes>
  )
}
