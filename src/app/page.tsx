'use client';

import dynamic from 'next/dynamic';

const PDFApp = dynamic(() => import('@/components/pdf/PDFApp'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-screen w-screen bg-[#1e1e1e]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-12 h-12 border-4 border-[#e8720c] border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-[#999]">Loading Foxit PDF Clone...</p>
      </div>
    </div>
  ),
});

export default function Home() {
  return <PDFApp />;
}
