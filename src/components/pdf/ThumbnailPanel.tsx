'use client';

import React, { useEffect, useRef, useCallback } from 'react';
import { usePDFStore } from './PDFStore';
import { pdfjsLib, initPDFWorker } from './PDFWorker';

export default function ThumbnailPanel() {
  const { numPages, currentPage, goToPage, document, zoom } = usePDFStore();
  const canvasRefs = useRef<Map<number, HTMLCanvasElement>>(new Map());
  const pdfDocRef = useRef<pdfjsLib.PDFDocumentProxy | null>(null);

  const renderThumbnail = useCallback(
    async (pageNum: number, canvas: HTMLCanvasElement) => {
      if (!document) return;

      try {
        initPDFWorker();
        const arrayBuffer = await document.arrayBuffer();
        const pdf = pdfDocRef.current || (await pdfjsLib.getDocument({ data: arrayBuffer }).promise);
        pdfDocRef.current = pdf;

        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: 0.3 });
        const context = canvas.getContext('2d');

        canvas.width = viewport.width;
        canvas.height = viewport.height;

        if (context) {
          await page.render({
            canvasContext: context,
            viewport: viewport,
          }).promise;
        }
      } catch (err) {
        console.error('Thumbnail render error:', err);
      }
    },
    [document]
  );

  useEffect(() => {
    return () => {
      pdfDocRef.current = null;
    };
  }, [document]);

  useEffect(() => {
    if (!document) return;

    const renderAll = async () => {
      initPDFWorker();
      try {
        const arrayBuffer = await document.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        pdfDocRef.current = pdf;

        for (let i = 1; i <= numPages; i++) {
          const canvas = canvasRefs.current.get(i);
          if (canvas) {
            await renderThumbnail(i, canvas);
          }
        }
      } catch (err) {
        console.error('Thumbnail batch render error:', err);
      }
    };

    renderAll();
  }, [document, numPages, renderThumbnail]);

  return (
    <div className="p-2 space-y-2">
      {Array.from({ length: numPages }, (_, i) => i + 1).map((pageNum) => (
        <button
          key={pageNum}
          onClick={() => goToPage(pageNum)}
          className={`w-full p-2 rounded cursor-pointer transition-all ${
            currentPage === pageNum
              ? 'bg-[#e8720c]/20 border-2 border-[#e8720c]'
              : 'hover:bg-[#3c3c3c] border-2 border-transparent'
          }`}
        >
          <div className="flex flex-col items-center gap-1">
            <div className="bg-white shadow-md rounded-sm overflow-hidden">
              <canvas
                ref={(el) => {
                  if (el) canvasRefs.current.set(pageNum, el);
                }}
                className="block"
              />
            </div>
            <span
              className={`text-xs ${
                currentPage === pageNum ? 'text-[#e8720c] font-semibold' : 'text-[#999]'
              }`}
            >
              {pageNum}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}
