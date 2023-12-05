import { Inter } from 'next/font/google'
import './globals.css'
import ActionsMenu from '@/app/components/actions-menu'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Football Matches AI',
  description: '',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ActionsMenu />
        {children}
        </body>
    </html>
  )
}
