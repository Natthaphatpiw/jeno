import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Jenosize Article Generator',
  description: 'AI-powered content generation for business trends and future ideas',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-navy-50">
          <header className="bg-gradient-to-r from-dark-navy-900 via-navy-800 to-dark-navy-800 shadow-2xl relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-sky-500/10 to-navy-500/10"></div>
            <div className="container-custom relative">
              <div className="flex flex-col lg:flex-row justify-between items-center py-12 gap-6">
                <div className="flex items-center space-x-6">
                  <div className="icon-wrapper w-16 h-16">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h1 className="text-4xl lg:text-5xl font-bold text-white">
                      Jenosize
                    </h1>
                    <p className="text-sky-300 text-lg font-medium mt-1">
                      AI Article Generator
                    </p>
                  </div>
                </div>
                <div className="text-center lg:text-right">
                  <div className="text-lg font-semibold text-sky-300 mb-2">
                    AI-powered content creation
                  </div>
                  <div className="flex flex-wrap justify-center lg:justify-end gap-4 text-sm">
                    <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-white">Professional</span>
                    <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-white">Innovative</span>
                    <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-white">Reliable</span>
                  </div>
                </div>
              </div>
            </div>
          </header>
          
          <main className="container-custom py-12">
            {children}
          </main>
        </div>
        
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </body>
    </html>
  );
}