'use client';

import React from 'react';
import {
  MessageSquare,
  Highlighter,
  Type,
  Pencil,
  Stamp,
  Trash2,
  Clock,
  Underline,
  Strikethrough,
} from 'lucide-react';
import { usePDFStore, Annotation, AnnotationType } from './PDFStore';

const annotationIcons: Record<AnnotationType, React.ReactNode> = {
  none: null,
  highlight: <Highlighter className="h-4 w-4 text-yellow-400" />,
  text: <Type className="h-4 w-4 text-green-400" />,
  draw: <Pencil className="h-4 w-4 text-red-400" />,
  stamp: <Stamp className="h-4 w-4 text-purple-400" />,
  underline: <Underline className="h-4 w-4 text-blue-400" />,
  strikethrough: <Strikethrough className="h-4 w-4 text-red-300" />,
};

const annotationColors: Record<AnnotationType, string> = {
  none: '#666',
  highlight: '#FFEB3B',
  text: '#4CAF50',
  draw: '#FF0000',
  stamp: '#9C27B0',
  underline: '#2196F3',
  strikethrough: '#F44336',
};

function AnnotationItem({ annotation }: { annotation: Annotation }) {
  const { removeAnnotation, selectedAnnotation, setSelectedAnnotation, goToPage } = usePDFStore();

  const isSelected = selectedAnnotation === annotation.id;
  const timeStr = new Date(annotation.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      onClick={() => {
        setSelectedAnnotation(annotation.id);
        goToPage(annotation.pageNumber);
      }}
      className={`p-2.5 rounded cursor-pointer transition-colors ${
        isSelected ? 'bg-[#e8720c]/20 border border-[#e8720c]' : 'hover:bg-[#3c3c3c] border border-transparent'
      }`}
    >
      <div className="flex items-start gap-2">
        <div
          className="mt-0.5 shrink-0 w-6 h-6 rounded flex items-center justify-center"
          style={{ backgroundColor: annotationColors[annotation.type] + '22' }}
        >
          {annotationIcons[annotation.type]}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-[#d4d4d4] capitalize">
              {annotation.type}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeAnnotation(annotation.id);
              }}
              className="p-0.5 rounded hover:bg-[#555] cursor-pointer"
            >
              <Trash2 className="h-3 w-3 text-[#666] hover:text-[#e55]" />
            </button>
          </div>
          {annotation.content && (
            <p className="text-xs text-[#999] mt-1 truncate">{annotation.content}</p>
          )}
          <div className="flex items-center gap-2 mt-1">
            <Clock className="h-3 w-3 text-[#555]" />
            <span className="text-[10px] text-[#555]">Page {annotation.pageNumber} · {timeStr}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnnotationPanel() {
  const { annotations } = usePDFStore();

  if (annotations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-[#666] px-4">
        <MessageSquare className="h-8 w-8 mb-2 opacity-40" />
        <p className="text-sm text-center">No annotations yet</p>
        <p className="text-xs text-[#555] mt-1">Use the toolbar to add highlights, notes, and more</p>
      </div>
    );
  }

  // Group annotations by page
  const grouped = annotations.reduce<Record<number, Annotation[]>>((acc, ann) => {
    if (!acc[ann.pageNumber]) acc[ann.pageNumber] = [];
    acc[ann.pageNumber].push(ann);
    return acc;
  }, {});

  return (
    <div className="p-2 space-y-3">
      {Object.entries(grouped).map(([page, items]) => (
        <div key={page}>
          <div className="text-[10px] font-semibold text-[#666] uppercase tracking-wide px-3 py-1">
            Page {page}
          </div>
          <div className="space-y-1">
            {items.map((annotation) => (
              <AnnotationItem key={annotation.id} annotation={annotation} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
