import type { ChatMessage as Msg } from '../../api/client'
import { CpuChipIcon, UserIcon } from '@heroicons/react/24/solid'

interface Props {
  message: Msg
}

export default function ChatMessage({ message }: Props) {
  const isAgent = message.role === 'assistant'

  return (
    <div className={`flex gap-3 ${isAgent ? '' : 'flex-row-reverse'}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white
        ${isAgent ? 'bg-indigo-600' : 'bg-gray-700'}`}>
        {isAgent ? <CpuChipIcon className="w-4 h-4" /> : <UserIcon className="w-4 h-4" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap
        ${isAgent
          ? 'bg-gray-800 text-gray-100 rounded-tl-sm'
          : 'bg-indigo-600 text-white rounded-tr-sm'
        }`}>
        {message.content}
      </div>
    </div>
  )
}
