import { useEffect, useMemo, useState, type ReactNode } from 'react'
import { useTranslation } from 'react-i18next'
import { Save } from 'lucide-react'

import { Card } from '@/components/ui/Card'
import { Chip } from '@/components/ui/Chip'
import { useUpdateProfile } from '@/hooks/useAnalysis'
import { ALLERGIES, CONDITIONS } from '@/lib/constants'
import { useAppStore } from '@/store/useAppStore'
import { useUserStore } from '@/store/useUserStore'
import { cn } from '@/lib/utils'

const LANG_OPTIONS: { code: string; label: string }[] = [
  { code: 'uz', label: "O'zbekcha" },
  { code: 'ru', label: 'Русский' },
  { code: 'en', label: 'English' },
]

const THEME_OPTIONS = [
  { value: 'system', i18n: 'profile.theme_system' },
  { value: 'light', i18n: 'profile.theme_light' },
  { value: 'dark', i18n: 'profile.theme_dark' },
]

export function ProfilePage() {
  const { t, i18n } = useTranslation()
  const user = useUserStore((s) => s.user)
  const update = useUpdateProfile()
  const toast = useAppStore((s) => s.toast)

  const [age, setAge] = useState(user?.age?.toString() ?? '')
  const [height, setHeight] = useState(user?.height_cm?.toString() ?? '')
  const [weight, setWeight] = useState(user?.weight_kg?.toString() ?? '')
  const [conditions, setConditions] = useState<string[]>(user?.chronic_conditions ?? [])
  const [allergies, setAllergies] = useState<string[]>(user?.allergies ?? [])

  useEffect(() => {
    setConditions(user?.chronic_conditions ?? [])
    setAllergies(user?.allergies ?? [])
    setAge(user?.age?.toString() ?? '')
    setHeight(user?.height_cm?.toString() ?? '')
    setWeight(user?.weight_kg?.toString() ?? '')
  }, [user])

  const dirty = useMemo(() => {
    if (!user) return false
    return (
      age !== (user.age?.toString() ?? '') ||
      height !== (user.height_cm?.toString() ?? '') ||
      weight !== (user.weight_kg?.toString() ?? '') ||
      JSON.stringify([...conditions].sort()) !== JSON.stringify([...(user.chronic_conditions ?? [])].sort()) ||
      JSON.stringify([...allergies].sort()) !== JSON.stringify([...(user.allergies ?? [])].sort())
    )
  }, [age, height, weight, conditions, allergies, user])

  if (!user) return null

  const toggle = (list: string[], setList: (v: string[]) => void, v: string) =>
    setList(list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

  const save = async () => {
    try {
      await update.mutateAsync({
        age: age ? Number(age) : null,
        height_cm: height ? Number(height) : null,
        weight_kg: weight ? Number(weight) : null,
        chronic_conditions: conditions,
        allergies,
      })
      toast(t('profile.saved_toast'), 'success')
    } catch {
      toast(t('common.error'), 'error')
    }
  }

  const setLanguage = async (code: string) => {
    void i18n.changeLanguage(code)
    await update.mutateAsync({ language: code })
  }

  const setTheme = async (theme: string) => {
    await update.mutateAsync({ theme })
  }

  return (
    <div className="space-y-4">
      <header className="flex flex-col items-center gap-2 py-2 text-center">
        <span className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-[var(--tg-button)]/15 text-3xl">
          {user.photo_url ? (
            <img src={user.photo_url} alt="" className="h-20 w-20 object-cover" />
          ) : (
            (user.first_name?.[0] ?? '👤')
          )}
        </span>
        <div>
          <h1 className="text-xl font-bold">
            {user.first_name} {user.last_name}
          </h1>
          {user.username && <p className="text-sm text-[var(--tg-hint)]">@{user.username}</p>}
        </div>
        {user.daily_calorie_target && (
          <p className="text-xs text-[var(--tg-hint)]">
            {t('profile.calorie_target')}: {user.daily_calorie_target} kcal
          </p>
        )}
      </header>

      {/* Til */}
      <Section title={t('profile.language')}>
        <div className="flex gap-2">
          {LANG_OPTIONS.map((l) => (
            <button
              key={l.code}
              type="button"
              onClick={() => void setLanguage(l.code)}
              className={cn(
                'flex-1 rounded-xl border py-2.5 text-sm font-medium',
                user.language === l.code
                  ? 'border-[var(--tg-button)] bg-[var(--tg-button)]/10'
                  : 'border-black/10 dark:border-white/15',
              )}
            >
              {l.label}
            </button>
          ))}
        </div>
      </Section>

      {/* Tema */}
      <Section title={t('profile.theme')}>
        <div className="flex gap-2">
          {THEME_OPTIONS.map((th) => (
            <button
              key={th.value}
              type="button"
              onClick={() => void setTheme(th.value)}
              className={cn(
                'flex-1 rounded-xl border py-2.5 text-sm font-medium',
                user.theme === th.value
                  ? 'border-[var(--tg-button)] bg-[var(--tg-button)]/10'
                  : 'border-black/10 dark:border-white/15',
              )}
            >
              {t(th.i18n)}
            </button>
          ))}
        </div>
      </Section>

      {/* Shaxsiy ma'lumotlar */}
      <Section title={t('profile.personal')}>
        <div className="grid grid-cols-3 gap-3">
          <NumField label={t('profile.age')} value={age} onChange={setAge} />
          <NumField label={t('profile.height')} value={height} onChange={setHeight} />
          <NumField label={t('profile.weight')} value={weight} onChange={setWeight} />
        </div>
      </Section>

      {/* Kasalliklar */}
      <Section title={t('profile.conditions')}>
        <div className="flex flex-wrap gap-2">
          {conditions.length === 0 && <p className="text-sm text-[var(--tg-hint)]">{t('onboarding.none')}</p>}
          {CONDITIONS.map((c) => (
            <Chip key={c.value} active={conditions.includes(c.value)} onClick={() => toggle(conditions, setConditions, c.value)}>
              {t(c.i18n)}
            </Chip>
          ))}
        </div>
      </Section>

      {/* Allergiyalar */}
      <Section title={t('profile.allergies')}>
        <div className="flex flex-wrap gap-2">
          {allergies.length === 0 && <p className="text-sm text-[var(--tg-hint)]">{t('onboarding.none')}</p>}
          {ALLERGIES.map((a) => (
            <Chip key={a.value} active={allergies.includes(a.value)} onClick={() => toggle(allergies, setAllergies, a.value)}>
              {t(a.i18n)}
            </Chip>
          ))}
        </div>
      </Section>

      {/* Saqlash tugmasi */}
      {dirty && (
        <div className="sticky bottom-24 z-20">
          <button type="button" onClick={() => void save()} disabled={update.isPending} className="btn-primary w-full shadow-lg">
            <Save className="h-4 w-4" />
            {t('common.save')}
          </button>
        </div>
      )}
    </div>
  )
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card>
      <h2 className="mb-3 text-sm font-semibold text-[var(--tg-hint)]">{title}</h2>
      {children}
    </Card>
  )
}

function NumField({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="mb-1 block truncate text-[10px] text-[var(--tg-hint)]">{label}</span>
      <input
        type="number"
        inputMode="numeric"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border border-black/10 bg-transparent px-2 py-2.5 text-center text-sm outline-none focus:border-[var(--tg-button)] dark:border-white/15"
      />
    </label>
  )
}
