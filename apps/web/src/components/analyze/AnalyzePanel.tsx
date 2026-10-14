import { useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Camera, ImageIcon, Sparkles } from 'lucide-react'

import { ResultSheet } from '@/components/analyze/ResultSheet'
import { useAnalyze } from '@/hooks/useAnalysis'
import { tg } from '@/lib/telegram'
import type { Analysis } from '@/lib/types'

/** Rasm tanlash (kamera/galereya) + AI tahlil qilish paneli. */
export function AnalyzePanel({ autoOpenSheet = true }: { autoOpenSheet?: boolean }) {
  const { t } = useTranslation()
  const analyze = useAnalyze()

  const cameraRef = useRef<HTMLInputElement>(null)
  const galleryRef = useRef<HTMLInputElement>(null)

  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<Analysis | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)

  const onPick = (f: File | undefined) => {
    if (!f) return
    if (preview) URL.revokeObjectURL(preview)
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    tg.haptic('light')
  }

  const run = async () => {
    if (!file) return
    tg.haptic('medium')
    try {
      const analysis = await analyze.mutateAsync(file)
      setResult(analysis)
      if (autoOpenSheet) setSheetOpen(true)
      tg.notify(analysis.risk_level === 'dangerous' ? 'error' : 'success')
    } catch {
      tg.notify('error')
    }
  }

  const reset = () => {
    if (preview) URL.revokeObjectURL(preview)
    setFile(null)
    setPreview(null)
    setResult(null)
  }

  return (
    <div className="space-y-4">
      {/* Hidden inputs */}
      <input
        ref={cameraRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => onPick(e.target.files?.[0])}
      />
      <input
        ref={galleryRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => onPick(e.target.files?.[0])}
      />

      <div className="relative overflow-hidden rounded-3xl border border-dashed border-black/15 bg-black/[0.02] dark:border-white/15 dark:bg-white/5">
        {preview ? (
          <img src={preview} alt="preview" className="h-64 w-full object-cover" />
        ) : (
          <button
            type="button"
            onClick={() => cameraRef.current?.click()}
            className="flex h-64 w-full flex-col items-center justify-center gap-3 text-[var(--tg-hint)]"
          >
            <span className="rounded-full bg-[var(--tg-button)]/10 p-4 text-[var(--tg-button)]">
              <Camera className="h-8 w-8" />
            </span>
            <span className="text-sm font-medium">{t('analyze.drop_hint')}</span>
          </button>
        )}

        {analyze.isPending && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/60 text-white backdrop-blur-sm">
            <span className="h-10 w-10 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            <p className="text-sm font-semibold">{t('analyze.analyzing')}</p>
            <p className="text-xs opacity-80">{t('analyze.analyzing_hint')}</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <button type="button" onClick={() => cameraRef.current?.click()} className="btn-outline flex-col gap-1.5 py-4">
          <Camera className="h-5 w-5" />
          <span className="text-xs">{t('analyze.camera')}</span>
        </button>
        <button type="button" onClick={() => galleryRef.current?.click()} className="btn-outline flex-col gap-1.5 py-4">
          <ImageIcon className="h-5 w-5" />
          <span className="text-xs">{t('analyze.gallery')}</span>
        </button>
      </div>

      <div className="flex gap-3">
        {preview && (
          <button type="button" onClick={reset} className="btn-ghost">
            {t('common.cancel')}
          </button>
        )}
        <button
          type="button"
          onClick={run}
          disabled={!file || analyze.isPending}
          className="btn-primary flex-1"
        >
          <Sparkles className="h-4 w-4" />
          {t('nav.analyze')}
        </button>
      </div>

      {analyze.isError && (
        <p className="text-center text-sm text-rose-500">
          {(analyze.error as Error)?.message ?? t('common.error')}
        </p>
      )}

      <ResultSheet analysis={result} open={sheetOpen} onClose={() => setSheetOpen(false)} />
    </div>
  )
}
