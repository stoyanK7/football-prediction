import { Inter } from 'next/font/google';
import './globals.css';
import ActionsMenu from '@/app/components/actions-menu';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
    title: 'Football Matches AI',
    description: '',
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <Toaster
                    position="top-left"
                    reverseOrder={false}
                    toastOptions={{ duration: 5000 }}
                />
                <ActionsMenu />
                {children}
            </body>
        </html>
    );
}
