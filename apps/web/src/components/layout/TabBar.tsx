import { Camera, Clock, Home, User } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { NavLink } from 'react-router-dom'

import { tg } from '@/lib/telegram'
import { cn } from '@/lib/utils'

const items = [
  { to: '/', icon: Home, label: 'nav.home', end: true },
  { to: '/history', icon: Clock, label: 'nav.history', end: false },
  { to: '/analyze', icon: Camera, label: 'nav.analyze', center: true, end: false },
  { to: '/profile', icon: User, label: 'nav.profile', end: false },
]

/** Pastdagi asosiy navigatsiya paneli. */
export function TabBar() {
  const { t } = useTranslation()

  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-black/5 bg-[var(--tg-bg)]/95 backdrop-blur safe-bottom dark:border-white/10">
      <div className="mx-auto flex max-w-lg items-center justify-around px-2">
        {items.map(({ to, icon: Icon, label, center, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            onClick={() => tg.haptic('light')}
            className='flex flex-1 flex-col items-center gap-1 py-2.5 text-[11px] font-medium'
          >
            {({ isActive }) => (
              <span className="flex flex-1 flex-col items-center gap-1">
                <span
                  className={cn(
                    'flex items-center justify-center rounded-full transition',
                    center
                      ? '-mt-5 h-12 w-12 bg-[var(--tg-button)] text-[var(--tg-button-text)] shadow-md'
                      : 'h-8 w-8',
                    !center && (isActive ? 'bg-[var(--tg-button)]/10' : ''),
                  )}
                >
                  <Icon
                    className={cn(center ? 'h-6 w-6' : 'h-5 w-5')}
                    color={!center && isActive ? 'var(--tg-button)' : undefined}
                    style={!center && !isActive ? { color: 'var(--tg-hint)' } : undefined}
                  />
                </span>
                <span
                  className={center ? 'text-[var(--tg-button)]' : ''}
                  style={!center ? { color: isActive ? 'var(--tg-button)' : 'var(--tg-hint)' } : undefined}
                >
                  {t(label)}
                </span>
              </span>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
