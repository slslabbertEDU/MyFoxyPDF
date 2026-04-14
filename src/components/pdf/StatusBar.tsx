'use client';

import React from 'react';
import { usePDFStore } from './PDFStore';
import { FileText, ZoomIn, RotateCw, MessageSquare } from 'lucide-react';

export default function StatusBar() {
  const { currentPage, numPages, zoom, rotation, document, annotations, viewMode, documentName } = usePDFStore();

  const zoomPercent = Math.round(zoom * 100);
  const viewModeLabel = viewMode === 'single' ? 'Single' : viewMode === 'continuous' ? 'Continuous' : viewMode === 'facing' ? 'Facing' : 'Facing Continuous';

  return (
    <div className="flex items-center h-6 bg-[#2d2d2d] border-t border-[#1a1a1a] px-2 text-[10px] text-[#777] select-none">
      <div className="flex items-center gap-3">
        {document && (
          <div className="flex items-center gap-1">
            <FileText className="h-3 w-3 text-[#e8720c]" />
            <span className="text-[#999] truncate max-w-[200px]">{documentName}</span>
          </div>
        )}
        <span>
          Page {document ? currentPage : 0} / {numPages}
        </span>
        <div className="flex items-center gap-1">
          <ZoomIn className="h-3 w-3" />
          <span>{zoomPercent}%</span>
        </div>
        {rotation !== 0 && (
          <div className="flex items-center gap-1">
            <RotateCw className="h-3 w-3" />
            <span>{rotation}°</span>
          </div>
        )}
        <span className="text-[#555]">{viewModeLabel}</span>
      </div>
      <div className="flex-1" />
      <div className="flex items-center gap-3">
        {annotations.length > 0 && (
          <div className="flex items-center gap-1">
            <MessageSquare className="h-3 w-3" />
            <span>{annotations.length} annotation{annotations.length !== 1 ? 's' : ''}</span>
          </div>
        )}
        <span className="text-[#e8720c] font-semibold text-[11px]">Foxit PDF</span>
      </div>
    </div>
  );
}
