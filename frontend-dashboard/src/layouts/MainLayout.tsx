import type { ReactNode } from 'react';

export default function MainLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col relative z-0">
      <main className="flex-grow p-8">
        {children}
      </main>
    </div>
  );
}
