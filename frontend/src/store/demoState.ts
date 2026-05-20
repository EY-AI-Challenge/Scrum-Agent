import { create } from 'zustand'
import type { AgentState } from '../types/demo_state'
import { fetchAgentState } from '../api/client'

interface DemoStore {
  state: AgentState | null
  loading: boolean
  error: string | null
  load: () => Promise<void>
}

export const useDemoStore = create<DemoStore>((set, get) => ({
  state: null,
  loading: false,
  error: null,
  load: async () => {
    if (get().state || get().loading) return
    set({ loading: true, error: null })
    try {
      const data = await fetchAgentState()
      set({ state: data, loading: false })
    } catch (err) {
      set({ error: (err as Error).message, loading: false })
    }
  },
}))
