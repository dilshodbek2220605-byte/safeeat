import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import '@/i18n'
import { RiskBadge } from '@/components/ui/RiskBadge'

describe('RiskBadge', () => {
  it('renders safe level', () => {
    render(<RiskBadge level="safe" />)
    expect(screen.getByText(/🟢/)).toBeInTheDocument()
  })

  it('renders dangerous level with red dot', () => {
    const { container } = render(<RiskBadge level="dangerous" />)
    expect(container.textContent).toContain('🔴')
  })

  it('defaults to safe when level is null', () => {
    const { container } = render(<RiskBadge level={null} />)
    expect(container.textContent).toContain('🟢')
  })
})
