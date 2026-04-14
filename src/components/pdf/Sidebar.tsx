'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  LayoutGrid,
  Bookmark,
  Search,
  MessageSquare,
  ChevronRight,
  FileText,
} from 'lucide-react';
import { usePDFStore, SidebarTab } from './PDFStore';
import ThumbnailPanel from './ThumbnailPanel';
import BookmarkPanel from './BookmarkPanel';
import SearchPanel from './SearchPanel';
import AnnotationPanel from './AnnotationPanel';

export default function Sidebar() {
  const { sidebarOpen, sidebarTab, setSidebarTab, sidebarWidth, setSidebarWidth, pdfFile } = usePDFStore();
  const resizeRef = useRef<HTMLDivElement>(null);
  const [isResizing, setIsResizing] = useState(false);

  const tabs: { id: SidebarTab; icon: React.ReactNode; label: string }[] = [
    { id: 'thumbnails', icon: <LayoutGrid className="h-5 w-5" />, label: 'Pages' },
    { id: 'bookmarks', icon: <Bookmark className="h-5 w-5" />, label: 'Bookmarks' },
    { id: 'search', icon: <Search className="h-5 w-5" />, label: 'Search' },
    { id: 'annotations', icon: <MessageSquare className="h-5 w-5" />, label: 'Comments' },
  ];

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = Math.max(160, Math.min(400, e.clientX));
      setSidebarWidth(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, setSidebarWidth]);

  if (!sidebarOpen) return null;

  return (
    <div className="flex h-full select-none" style={{ width: sidebarWidth }}>
      {/* Tab strip */}
      <div className="flex flex-col items-center w-10 bg-[#252525] border-r border-[#1a1a1a] py-2 gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSidebarTab(tab.id)}
            className={`p-2 rounded cursor-pointer transition-colors ${
              sidebarTab === tab.id
                ? 'bg-[#e8720c] text-white'
                : 'text-[#999] hover:bg-[#3c3c3c] hover:text-[#d4d4d4]'
            }`}
            title={tab.label}
          >
            {tab.icon}
          </button>
        ))}
      </div>

      {/* Panel content */}
      <div className="flex-1 bg-[#2d2d2d] border-r border-[#1a1a1a] overflow-hidden flex flex-col">
        {/* Panel header */}
        <div className="flex items-center h-8 px-3 bg-[#333] border-b border-[#1a1a1a]">
          <span className="text-xs font-semibold text-[#d4d4d4] uppercase tracking-wide">
            {sidebarTab === 'thumbnails' && 'Page Thumbnails'}
            {sidebarTab === 'bookmarks' && 'Bookmarks'}
            {sidebarTab === 'search' && 'Search'}
            {sidebarTab === 'annotations' && 'Comments'}
          </span>
        </div>

        {/* Panel body */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar">
          {!pdfFile ? (
            <div className="flex flex-col items-center justify-center h-full text-[#666] px-4">
              <FileText className="h-12 w-12 mb-3 opacity-40" />
              <p className="text-sm text-center">Open a PDF file to see {sidebarTab}</p>
            </div>
          ) : (
            <>
              {sidebarTab === 'thumbnails' && <ThumbnailPanel />}
              {sidebarTab === 'bookmarks' && <BookmarkPanel />}
              {sidebarTab === 'search' && <SearchPanel />}
              {sidebarTab === 'annotations' && <AnnotationPanel />}
            </>
          )}
        </div>
      </div>

      {/* Resize handle */}
      <div
        ref={resizeRef}
        className="w-1 cursor-col-resize hover:bg-[#e8720c] active:bg-[#e8720c] transition-colors"
        onMouseDown={handleMouseDown}
      />
    </div>
  );
}
