'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { usePDFStore, BookmarkItem } from './PDFStore';
import { pdfjsLib, initPDFWorker } from './PDFWorker';
import PDFPage from './PDFPage';
import {
  FileText,
  Loader2,
  AlertCircle,
  FileUp,
} from 'lucide-react';

export default function PDFViewer() {
  const {
    pdfFile,
    numPages,
    setNumPages,
    isLoading,
    setIsLoading,
    error,
    setError,
    currentPage,
    goToPage,
    viewMode,
    setPdfFile,
    setDocumentName,
    setBookmarks,
    zoom,
    rotation,
    activeTool,
    addTab,
  } = usePDFStore();

  const [pdfDoc, setPdfDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Load PDF document
  const loadDocument = useCallback(async (file: File) => {
    setIsLoading(true);
    setError(null);
    setDocumentName(file.name);

    try {
      initPDFWorker();
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

      setPdfDoc(pdf);
      setNumPages(pdf.numPages);
      setPdfFile(file);

      // Add tab
      addTab({
        id: `tab-${Date.now()}`,
        name: file.name,
        pdfFile: file,
      });

      // Extract bookmarks
      try {
        const outline = await pdf.getOutline();
        if (outline) {
          const processOutline = async (items: pdfjsLib.OutlineItem[]): Promise<BookmarkItem[]> => {
            const result: BookmarkItem[] = [];
            for (const item of items) {
              let pageNumber = 1;
              if (item.dest) {
                try {
                  let dest = item.dest;
                  if (typeof dest === 'string') {
                    dest = (await pdf.getDestination(dest)) as unknown as any[];
                  }
                  if (dest && dest[0]) {
                    const pageRef = dest[0];
                    const pageIdx = await pdf.getPageIndex(pageRef);
                    pageNumber = pageIdx + 1;
                  }
                } catch (_e) {
                  // ignore bookmark errors
                }
              }
              const children = item.items ? await processOutline(item.items) : [];
              result.push({ title: item.title, pageNumber, children: children.length > 0 ? children : undefined });
            }
            return result;
          };
          const bookmarks = await processOutline(outline);
          setBookmarks(bookmarks);
        }
      } catch (_e) {
        // ignore bookmark extraction errors
      }
    } catch (err) {
      console.error('PDF load error:', err);
      setError('Failed to load PDF. The file may be corrupted or password-protected.');
    } finally {
      setIsLoading(false);
    }
  }, [setPdfFile, setDocumentName, setNumPages, setIsLoading, setError, setBookmarks, addTab]);

  // Load PDF from URL
  const loadDocumentFromUrl = useCallback(async (url: string, name: string) => {
    setIsLoading(true);
    setError(null);
    setDocumentName(name);

    try {
      initPDFWorker();
      const pdf = await pdfjsLib.getDocument(url).promise;

      setPdfDoc(pdf);
      setNumPages(pdf.numPages);

      // Create a placeholder File object
      const response = await fetch(url);
      const blob = await response.blob();
      const file = new File([blob], name, { type: 'application/pdf' });
      setPdfFile(file);

      // Add tab
      addTab({
        id: `tab-${Date.now()}`,
        name: name,
        pdfFile: file,
      });

      // Extract bookmarks
      try {
        const outline = await pdf.getOutline();
        if (outline) {
          const processOutline = async (items: pdfjsLib.OutlineItem[]): Promise<BookmarkItem[]> => {
            const result: BookmarkItem[] = [];
            for (const item of items) {
              let pageNumber = 1;
              if (item.dest) {
                try {
                  let dest = item.dest;
                  if (typeof dest === 'string') {
                    dest = (await pdf.getDestination(dest)) as unknown as any[];
                  }
                  if (dest && dest[0]) {
                    const pageRef = dest[0];
                    const pageIdx = await pdf.getPageIndex(pageRef);
                    pageNumber = pageIdx + 1;
                  }
                } catch (_e) {
                  // ignore bookmark errors
                }
              }
              const children = item.items ? await processOutline(item.items) : [];
              result.push({ title: item.title, pageNumber, children: children.length > 0 ? children : undefined });
            }
            return result;
          };
          const bookmarks = await processOutline(outline);
          setBookmarks(bookmarks);
        }
      } catch (_e) {
        // ignore bookmark extraction errors
      }
    } catch (err) {
      console.error('PDF load error:', err);
      setError('Failed to load PDF. The file may be corrupted or password-protected.');
    } finally {
      setIsLoading(false);
    }
  }, [setPdfFile, setDocumentName, setNumPages, setIsLoading, setError, setBookmarks, addTab]);

  // Auto-load sample PDF on mount
  useEffect(() => {
    loadDocumentFromUrl('/sample.pdf', 'sample.pdf');
  }, [loadDocumentFromUrl]);

  // Listen for file open events
  useEffect(() => {
    const handleFileOpen = (e: Event) => {
      const file = (e as CustomEvent<File>).detail;
      if (file) loadDocument(file);
    };

    window.addEventListener('pdf-file-open', handleFileOpen);
    return () => window.removeEventListener('pdf-file-open', handleFileOpen);
  }, [loadDocument]);

  // Handle drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file && file.type === 'application/pdf') {
        loadDocument(file);
      }
    },
    [loadDocument]
  );

  // Handle scroll for page tracking
  const handleScroll = useCallback(() => {
    if (!containerRef.current || !pdfDoc) return;

    const container = containerRef.current;
    const pageElements = container.querySelectorAll('[data-page-number]');

    for (let i = 0; i < pageElements.length; i++) {
      const el = pageElements[i] as HTMLElement;
      const rect = el.getBoundingClientRect();
      const containerRect = container.getBoundingClientRect();

      if (rect.top >= containerRect.top && rect.top <= containerRect.top + containerRect.height / 2) {
        const pageNum = parseInt(el.getAttribute('data-page-number') || '1', 10);
        if (pageNum !== currentPage) {
          goToPage(pageNum);
        }
        break;
      }
    }
  }, [pdfDoc, currentPage, goToPage]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'f':
            e.preventDefault();
            usePDFStore.getState().setIsSearchVisible(true);
            usePDFStore.getState().setSidebarTab('search');
            if (!usePDFStore.getState().sidebarOpen) {
              usePDFStore.getState().setSidebarOpen(true);
            }
            break;
          case 'o':
            e.preventDefault();
            const input = globalThis.document.createElement('input');
            input.type = 'file';
            input.accept = '.pdf';
            input.onchange = (ev) => {
              const file = (ev.target as HTMLInputElement).files?.[0];
              if (file) loadDocument(file);
            };
            input.click();
            break;
          case '=':
          case '+':
            e.preventDefault();
            usePDFStore.getState().zoomIn();
            break;
          case '-':
            e.preventDefault();
            usePDFStore.getState().zoomOut();
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loadDocument]);

  const cursorClass = activeTool === 'hand' ? 'cursor-grab' : activeTool === 'draw' ? 'cursor-crosshair' : activeTool !== 'select' ? 'cursor-crosshair' : '';

  // Helper to open file picker
  const openFilePicker = useCallback(() => {
    const input = globalThis.document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) loadDocument(file);
    };
    input.click();
  }, [loadDocument]);

  // Empty state - no pdfFile
  if (!pdfFile && !isLoading) {
    return (
      <div
        ref={containerRef}
        className={`flex-1 flex items-center justify-center bg-[#1e1e1e] ${
          isDragging ? 'bg-[#2a2a2a]' : ''
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center gap-6 text-center px-8">
          {isDragging ? (
            <>
              <div className="w-24 h-24 rounded-full bg-[#e8720c]/20 flex items-center justify-center">
                <FileUp className="h-12 w-12 text-[#e8720c]" />
              </div>
              <div>
                <p className="text-lg font-semibold text-[#e8720c]">Drop your PDF here</p>
                <p className="text-sm text-[#999] mt-1">Release to open the document</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-28 h-28 rounded-2xl bg-[#2a2a2a] border border-[#3a3a3a] flex items-center justify-center">
                <FileText className="h-14 w-14 text-[#555]" />
              </div>
              <div>
                <p className="text-xl font-semibold text-[#d4d4d4]">Open a PDF Document</p>
                <p className="text-sm text-[#888] mt-2 max-w-md leading-relaxed">
                  Drag and drop a PDF file here, or click the Open button to get started.
                  You can also use <kbd className="px-1.5 py-0.5 bg-[#333] rounded text-xs text-[#d4d4d4]">Ctrl+O</kbd> to open a file.
                </p>
              </div>
              <button
                onClick={openFilePicker}
                className="px-6 py-2.5 bg-[#e8720c] hover:bg-[#d4680a] text-white text-sm font-medium rounded-lg transition-colors cursor-pointer shadow-lg shadow-[#e8720c]/20"
              >
                Open PDF File
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#1e1e1e]">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-14 h-14 border-3 border-[#333] rounded-full" />
            <div className="absolute top-0 left-0 w-14 h-14 border-3 border-[#e8720c] border-t-transparent rounded-full animate-spin" />
          </div>
          <p className="text-sm text-[#888]">Loading document...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#1e1e1e]">
        <div className="flex flex-col items-center gap-4 text-center px-8">
          <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
            <AlertCircle className="h-8 w-8 text-red-400" />
          </div>
          <p className="text-sm text-red-400 max-w-md">{error}</p>
          <button
            onClick={() => {
              setError(null);
              openFilePicker();
            }}
            className="px-5 py-2 bg-[#e8720c] hover:bg-[#d4680a] text-white text-sm rounded-lg transition-colors cursor-pointer"
          >
            Try Another File
          </button>
        </div>
      </div>
    );
  }

  // Render pages based on view mode
  const pagesToRender = viewMode === 'single' ? [currentPage] : Array.from({ length: numPages }, (_, i) => i + 1);

  return (
    <div
      ref={containerRef}
      className={`flex-1 overflow-auto bg-[#1e1e1e] custom-scrollbar ${cursorClass}`}
      onScroll={handleScroll}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex flex-col items-center py-4">
        {pagesToRender.map((pageNum) => (
          <div
            key={`${pageNum}-${zoom}-${rotation}`}
            data-page-number={pageNum}
            className="relative"
          >
            <PDFPage pageNumber={pageNum} pdfDoc={pdfDoc} />
          </div>
        ))}
      </div>
    </div>
  );
}
