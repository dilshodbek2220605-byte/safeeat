import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeft, Check } from 'lucide-react'

import { Chip } from '@/components/ui/Chip'
import { api } from '@/lib/api'
import { ALLERGIES, CONDITIONS } from '@/lib/constants'
import type { User } from '@/lib/types'
import { useUserStore } from '@/store/useUserStore'
import { cn } from '@/lib/utils'

/** Ko'p qadamli onboarding: til → profil → kasalliklar → allergiyalar → maqsad. */
export function OnboardingFlow() {
  const { t, i18n } = useTranslation()
  const setUser = useUserStore((s) => s.setUser)

  const [step, setStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)

  const [language, setLanguage] = useState(i18n.language)
  const [age, setAge] = useState('')
  const [gender, setGender] = useState<string | null>(null)
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [conditions, setConditions] = useState<string[]>([])
  const [allergies, setAllergies] = useState<string[]>([])
  const [goal, setGoal] = useState<string | null>(null)

  const steps = useMemo(
    () =>
      [
        { key: 'language', title: t('onboarding.step_language') },
        { key: 'about', title: t('onboarding.step_about') },
        { key: 'health', title: t('onboarding.step_health') },
        { key: 'allergies', title: t('onboarding.step_allergies') },
        { key: 'goal', title: t('onboarding.step_goal') },
      ] as const,
    [t],
  )

  const changeLanguage = (code: string) => {
    setLanguage(code)
    void i18n.changeLanguage(code)
  }

  const toggle = (list: string[], setList: (v: string[]) => void, value: string) =>
    setList(list.includes(value) ? list.filter((v) => v !== value) : [...list, value])

  const isLast = step === steps.length - 1
  const canNext = step !== 4 || !!goal

  const submit = async () => {
    setSubmitting(true)
    try {
      const user = await api.post<User>('/api/v1/users/me/onboarding', {
        language,
        age: age ? Number(age) : null,
        gender,
        height_cm: height ? Number(height) : null,
        weight_kg: weight ? Number(weight) : null,
        chronic_conditions: conditions,
        allergies,
        goal,
      })
      setUser(user)
    } catch {
      // Xatolik bo'lsa onboarding'da qolamiz
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-full flex-col bg-[var(--tg-bg)] px-5 pb-8 pt-6 safe-top">
      <div className="mb-6 flex items-center gap-2">
        {step > 0 && (
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-black/5 dark:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
        )}
        <div className="flex flex-1 gap-1.5">
          {steps.map((_, i) => (
            <span
              key={i}
              className={
                'h-1.5 flex-1 rounded-full transition-colors ' +
                (i <= step ? 'bg-[var(--tg-button)]' : 'bg-black/10 dark:bg-white/10')
              }
            />
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
          className="flex-1"
        >
          <h1 className="mb-4 text-2xl font-bold">{steps[step].title}</h1>

          {step === 0 && <LanguageStep selected={language} onSelect={changeLanguage} />}
          {step === 1 && (
            <AboutStep
              age={age}
              setAge={setAge}
              gender={gender}
              setGender={setGender}
              height={height}
              setHeight={setHeight}
              weight={weight}
              setWeight={setWeight}
            />
          )}
          {step === 2 && (
            <ChipsStep
              question={t('onboarding.health_question')}
              hint={t('onboarding.health_hint')}
              options={CONDITIONS.map((c) => ({ value: c.value, label: t(c.i18n) }))}
              selected={conditions}
              onToggle={(v) => toggle(conditions, setConditions, v)}
            />
          )}
          {step === 3 && (
            <ChipsStep
              question={t('onboarding.allergies_question')}
              hint={t('onboarding.allergies_hint')}
              options={ALLERGIES.map((c) => ({ value: c.value, label: t(c.i18n) }))}
              selected={allergies}
              onToggle={(v) => toggle(allergies, setAllergies, v)}
              emphasize
            />
          )}
          {step === 4 && <GoalStep goal={goal} setGoal={setGoal} />}
        </motion.div>
      </AnimatePresence>

      <div className="mt-6">
        <button
          type="button"
          disabled={!canNext || submitting}
          onClick={() => (isLast ? void submit() : setStep((s) => s + 1))}
          className="btn-primary w-full"
        >
          {isLast ? (submitting ? t('common.loading') : t('onboarding.finish')) : t('common.continue')}
        </button>
      </div>
    </div>
  )
}

function LanguageStep({ selected, onSelect }: { selected: string; onSelect: (code: string) => void }) {
  const langs = [
    { code: 'uz', label: "O'zbekcha", flag: '🇺🇿' },
    { code: 'ru', label: 'Русский', flag: '🇷🇺' },
    { code: 'en', label: 'English', flag: '🇬🇧' },
  ]
  return (
    <div className="space-y-3">
      {langs.map((l) => (
        <button
          key={l.code}
          type="button"
          onClick={() => onSelect(l.code)}
          className={
            'flex w-full items-center gap-3 rounded-2xl border p-4 text-left transition ' +
            (selected === l.code
              ? 'border-[var(--tg-button)] bg-[var(--tg-button)]/10'
              : 'border-black/10 dark:border-white/15')
          }
        >
          <span className="text-2xl">{l.flag}</span>
          <span className="flex-1 font-medium">{l.label}</span>
          {selected === l.code && <Check className="h-5 w-5 text-[var(--tg-button)]" />}
        </button>
      ))}
    </div>
  )
}

function AboutStep(props: {
  age: string
  setAge: (v: string) => void
  gender: string | null
  setGender: (v: string) => void
  height: string
  setHeight: (v: string) => void
  weight: string
  setWeight: (v: string) => void
}) {
  const { t } = useTranslation()
  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--tg-hint)]">{t('onboarding.about_question')}</p>
      <div className="grid grid-cols-3 gap-3">
        <Field label={t('onboarding.age')} value={props.age} onChange={props.setAge} />
        <Field label={t('onboarding.height')} value={props.height} onChange={props.setHeight} />
        <Field label={t('onboarding.weight')} value={props.weight} onChange={props.setWeight} />
      </div>
      <div>
        <p className="mb-2 text-sm font-medium">{t('onboarding.gender')}</p>
        <div className="flex gap-2">
          {[
            { v: 'male', l: t('profile.gender_male') },
            { v: 'female', l: t('profile.gender_female') },
            { v: 'other', l: t('profile.gender_other') },
          ].map((g) => (
            <button
              key={g.v}
              type="button"
              onClick={() => props.setGender(g.v)}
              className={
                'flex-1 rounded-xl border py-3 text-sm font-medium ' +
                (props.gender === g.v
                  ? 'border-[var(--tg-button)] bg-[var(--tg-button)]/10'
                  : 'border-black/10 dark:border-white/15')
              }
            >
              {g.l}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function ChipsStep(props: {
  question: string
  hint?: string
  options: { value: string; label: string }[]
  selected: string[]
  onToggle: (v: string) => void
  emphasize?: boolean
}) {
  return (
    <div>
      <p className="mb-1 text-sm font-medium">{props.question}</p>
      {props.hint && <p className="mb-4 text-xs text-[var(--tg-hint)]">{props.hint}</p>}
      <div className={'flex flex-wrap gap-2 ' + (props.emphasize ? 'rounded-2xl bg-amber-500/10 p-3' : '')}>
        {props.options.map((o) => (
          <Chip key={o.value} active={props.selected.includes(o.value)} onClick={() => props.onToggle(o.value)}>
            {o.label}
          </Chip>
        ))}
      </div>
    </div>
  )
}

function GoalStep({ goal, setGoal }: { goal: string | null; setGoal: (v: string) => void }) {
  const { t } = useTranslation()
  const goals = [
    { v: 'lose_weight', emoji: '📉', l: t('profile.goal_lose') },
    { v: 'maintain', emoji: '⚖️', l: t('profile.goal_maintain') },
    { v: 'gain_weight', emoji: '📈', l: t('profile.goal_gain') },
    { v: 'health', emoji: '❤️', l: t('profile.goal_health') },
  ]
  return (
    <div className="space-y-3">
      {goals.map((g) => (
        <button
          key={g.v}
          type="button"
          onClick={() => setGoal(g.v)}
          className={
            'flex w-full items-center gap-3 rounded-2xl border p-4 text-left ' +
            (goal === g.v
              ? 'border-[var(--tg-button)] bg-[var(--tg-button)]/10'
              : 'border-black/10 dark:border-white/15')
          }
        >
          <span className="text-2xl">{g.emoji}</span>
          <span className="flex-1 font-medium">{g.l}</span>
          {goal === g.v && <Check className="h-5 w-5 text-[var(--tg-button)]" />}
        </button>
      ))}
    </div>
  )
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="mb-1 block truncate text-[10px] text-[var(--tg-hint)]">{label}</span>
      <input
        type="number"
        inputMode="numeric"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn(
          'w-full rounded-xl border border-black/10 bg-transparent px-2 py-2.5 text-center text-sm',
          'outline-none focus:border-[var(--tg-button)] dark:border-white/15',
        )}
      />
    </label>
  )
}
