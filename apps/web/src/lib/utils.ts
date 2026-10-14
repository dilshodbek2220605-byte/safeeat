import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Tailwind klasslarini xavfsiz birlashtirish. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
