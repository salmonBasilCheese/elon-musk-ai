import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Elon Musk AI - 戦略的対話エンジン',
    description: 'イーロン・マスクの思考スタイルで回答するAI。ビジネス、技術、人生の悩みまで対応。',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="ja">
            <body>{children}</body>
        </html>
    )
}
