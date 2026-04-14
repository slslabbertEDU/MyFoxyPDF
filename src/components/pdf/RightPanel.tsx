'use client';

import React, { useState } from 'react';
import { usePDFStore, AnnotationType } from './PDFStore';
import {
  MessageSquare,
  FileText,
  Info,
  User,
  HardDrive,
  StickyNote,
  Plus,
  Trash2,
  Highlighter,
  Type,
  Pencil,
  Stamp,
  Underline,
  Strikethrough,
  Palette,
} from 'lucide-react';

type RightPanelTab = 'comments' | 'properties';

const annotationTypeIcons: Record<string, React.ReactNode> = {
  highlight: <Highlighter className="h-3 w-3" />,
  text: <Type className="h-3 w-3" />,
  draw: <Pencil className="h-3 w-3" />,
  stamp: <Stamp className="h-3 w-3" />,
  underline: <Underline className="h-3 w-3" />,
  strikethrough: <Strikethrough className="h-3 w-3" />,
};

const annotationTypeColors: Record<string, string> = {
  highlight: '#FFEB3B',
  text: '#4CAF50',
  draw: '#FF0000',
  stamp: '#9C27B0',
  underline: '#2196F3',
  strikethrough: '#F44336',
};

export default function RightPanel() {
  const {
    rightPanelOpen,
    rightPanelWidth,
    document,
    documentName,
    numPages,
    annotations,
    addAnnotation,
    removeAnnotation,
    selectedAnnotation,
    setSelectedAnnotation,
    setActiveTool,
  } = usePDFStore();

  const [activeTab, setActiveTab] = useState<RightPanelTab>('comments');
  const [newComment, setNewComment] = useState('');
  const [commentType, setCommentType] = useState<AnnotationType>('text');

  if (!rightPanelOpen) return null;

  const commentAnnotations = annotations.filter((a) => a.type === 'text' || a.type === 'highlight');

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    addAnnotation({
      id: `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: commentType,
      pageNumber: usePDFStore.getState().currentPage,
      x: 50,
      y: 50,
      width: 25,
      height: 3,
      content: newComment.trim(),
      color: annotationTypeColors[commentType],
      timestamp: Date.now(),
    });
    setNewComment('');
  };

  return (
    <div
      className="flex flex-col h-full bg-[#2d2d2d] border-l border-[#1a1a1a] select-none"
      style={{ width: rightPanelWidth }}
    >
      {/* Tab selector */}
      <div className="flex items-center h-8 bg-[#333] border-b border-[#1a1a1a]">
        <button
          onClick={() => setActiveTab('comments')}
          className={`flex-1 h-full text-xs font-medium cursor-pointer transition-colors ${
            activeTab === 'comments'
              ? 'text-[#e8720c] border-b-2 border-[#e8720c] bg-[#2d2d2d]'
              : 'text-[#999] hover:text-[#d4d4d4]'
          }`}
        >
          Comments
        </button>
        <button
          onClick={() => setActiveTab('properties')}
          className={`flex-1 h-full text-xs font-medium cursor-pointer transition-colors ${
            activeTab === 'properties'
              ? 'text-[#e8720c] border-b-2 border-[#e8720c] bg-[#2d2d2d]'
              : 'text-[#999] hover:text-[#d4d4d4]'
          }`}
        >
          Properties
        </button>
      </div>

      {/* Comments tab */}
      {activeTab === 'comments' && (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Add comment */}
          <div className="p-3 border-b border-[#1a1a1a]">
            {/* Comment type selector */}
            <div className="flex items-center gap-1 mb-2">
              {(['highlight', 'text', 'underline', 'strikethrough'] as AnnotationType[]).map((type) => (
                <button
                  key={type}
                  onClick={() => setCommentType(type)}
                  className={`p-1 rounded cursor-pointer transition-colors ${
                    commentType === type ? 'bg-[#e8720c] text-white' : 'text-[#999] hover:bg-[#3c3c3c]'
                  }`}
                  title={type}
                >
                  {annotationTypeIcons[type]}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleAddComment();
                }}
                placeholder="Add a comment..."
                className="flex-1 h-8 px-3 text-sm bg-[#3c3c3c] border border-[#555] rounded text-[#d4d4d4] placeholder-[#666] focus:outline-none focus:border-[#e8720c]"
              />
              <button
                onClick={handleAddComment}
                className="p-1.5 bg-[#e8720c] hover:bg-[#d4680a] rounded cursor-pointer"
              >
                <Plus className="h-4 w-4 text-white" />
              </button>
            </div>
          </div>

          {/* Comment list */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
            {commentAnnotations.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-[#666]">
                <StickyNote className="h-8 w-8 mb-2 opacity-40" />
                <p className="text-xs text-center">No comments yet</p>
                <p className="text-[10px] text-[#555] mt-1">Add comments using the field above</p>
              </div>
            ) : (
              commentAnnotations.map((annotation) => (
                <div
                  key={annotation.id}
                  onClick={() => setSelectedAnnotation(annotation.id)}
                  className={`p-2.5 rounded text-sm cursor-pointer transition-colors ${
                    selectedAnnotation === annotation.id
                      ? 'bg-[#e8720c]/20 border border-[#e8720c]'
                      : 'hover:bg-[#3c3c3c] border border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2">
                      <div
                        className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                        style={{ backgroundColor: (annotationTypeColors[annotation.type] || '#666') + '33' }}
                      >
                        <span style={{ color: annotationTypeColors[annotation.type] || '#666' }}>
                          {annotationTypeIcons[annotation.type] || <MessageSquare className="h-3 w-3" />}
                        </span>
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs text-[#d4d4d4]">{annotation.content || `${annotation.type} annotation`}</p>
                        <p className="text-[10px] text-[#555] mt-1">
                          Page {annotation.pageNumber} · {new Date(annotation.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeAnnotation(annotation.id);
                      }}
                      className="p-0.5 rounded hover:bg-[#555] shrink-0 cursor-pointer"
                    >
                      <Trash2 className="h-3 w-3 text-[#555] hover:text-red-400" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Properties tab */}
      {activeTab === 'properties' && (
        <div className="flex-1 overflow-y-auto p-3 custom-scrollbar">
          {!document ? (
            <div className="flex flex-col items-center justify-center h-32 text-[#666]">
              <FileText className="h-8 w-8 mb-2 opacity-40" />
              <p className="text-xs text-center">No document open</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Document info */}
              <div>
                <h3 className="text-xs font-semibold text-[#999] uppercase tracking-wide mb-2">
                  Document Information
                </h3>
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-[#666] shrink-0" />
                    <div className="min-w-0">
                      <p className="text-[10px] text-[#666]">File Name</p>
                      <p className="text-xs text-[#d4d4d4] truncate">{documentName || 'Untitled'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <HardDrive className="h-4 w-4 text-[#666] shrink-0" />
                    <div>
                      <p className="text-[10px] text-[#666]">File Size</p>
                      <p className="text-xs text-[#d4d4d4]">
                        {document ? `${(document.size / 1024).toFixed(1)} KB` : 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Info className="h-4 w-4 text-[#666] shrink-0" />
                    <div>
                      <p className="text-[10px] text-[#666]">Pages</p>
                      <p className="text-xs text-[#d4d4d4]">{numPages}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Annotation summary */}
              <div>
                <h3 className="text-xs font-semibold text-[#999] uppercase tracking-wide mb-2">
                  Annotation Summary
                </h3>
                <div className="space-y-1.5">
                  {(['highlight', 'text', 'draw', 'stamp', 'underline', 'strikethrough'] as AnnotationType[]).map((type) => {
                    const count = annotations.filter((a) => a.type === type).length;
                    if (count === 0) return null;
                    return (
                      <div key={type} className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1.5">
                          <span style={{ color: annotationTypeColors[type] }}>
                            {annotationTypeIcons[type]}
                          </span>
                          <span className="text-[#999] capitalize">{type}</span>
                        </div>
                        <span className="text-[#d4d4d4]">{count}</span>
                      </div>
                    );
                  })}
                  {annotations.length === 0 && (
                    <p className="text-[10px] text-[#555]">No annotations</p>
                  )}
                </div>
              </div>

              {/* View info */}
              <div>
                <h3 className="text-xs font-semibold text-[#999] uppercase tracking-wide mb-2">
                  View Information
                </h3>
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#999]">Zoom Level</span>
                    <span className="text-[#d4d4d4]">{Math.round(usePDFStore.getState().zoom * 100)}%</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#999]">Rotation</span>
                    <span className="text-[#d4d4d4]">{usePDFStore.getState().rotation}°</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#999]">View Mode</span>
                    <span className="text-[#d4d4d4] capitalize">{usePDFStore.getState().viewMode}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
