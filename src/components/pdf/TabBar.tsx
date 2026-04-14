'use client';

import React, { useCallback } from 'react';
import { X, FileText, Plus } from 'lucide-react';
import { usePDFStore } from './PDFStore';

export default function TabBar() {
  const { tabs, activeTabId, setActiveTab, removeTab, document } = usePDFStore();

  const handleOpenFile = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const event = new CustomEvent('pdf-file-open', { detail: file });
        window.dispatchEvent(event);
      }
    };
    input.click();
  }, []);

  return (
    <div className="flex items-center h-8 bg-[#252525] border-b border-[#1a1a1a] select-none overflow-x-auto">
      {/* Foxit logo / brand */}
      <div className="flex items-center gap-1.5 px-3 border-r border-[#1a1a1a] shrink-0">
        <div className="w-4 h-4 bg-[#e8720c] rounded-sm flex items-center justify-center">
          <FileText className="h-3 w-3 text-white" />
        </div>
        <span className="text-xs font-semibold text-[#d4d4d4] tracking-tight">Foxit PDF</span>
      </div>

      {/* Document tabs */}
      <div className="flex items-center flex-1 overflow-x-auto">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3 h-full border-r border-[#1a1a1a] cursor-pointer group min-w-0 max-w-[180px] shrink-0 ${
              activeTabId === tab.id
                ? 'bg-[#1e1e1e] text-[#d4d4d4]'
                : 'bg-[#2a2a2a] text-[#888] hover:bg-[#333]'
            }`}
          >
            <FileText className="h-3.5 w-3.5 shrink-0 text-[#e8720c]" />
            <span className="text-xs truncate">{tab.name}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeTab(tab.id);
              }}
              className="ml-auto p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-[#4a4a4a] shrink-0 cursor-pointer"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        ))}

        {/* New tab button */}
        <button
          onClick={handleOpenFile}
          className="flex items-center justify-center w-8 h-full hover:bg-[#333] shrink-0 cursor-pointer"
          title="Open File"
        >
          <Plus className="h-3.5 w-3.5 text-[#888]" />
        </button>
      </div>

      {/* Current document name (when no tabs) */}
      {!tabs.length && document && (
        <div className="flex items-center gap-1.5 px-3 h-full bg-[#1e1e1e] text-[#d4d4d4]">
          <FileText className="h-3.5 w-3.5 text-[#e8720c]" />
          <span className="text-xs truncate">
            {usePDFStore.getState().documentName || 'Untitled'}
          </span>
        </div>
      )}
    </div>
  );
}
