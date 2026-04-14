'use client';

import React, { useEffect, useRef, useCallback, useLayoutEffect } from 'react';
import { usePDFStore } from './PDFStore';
import { pdfjsLib, initPDFWorker } from './PDFWorker';

interface PDFPageProps {
  pageNumber: number;
  pdfDoc: pdfjsLib.PDFDocumentProxy | null;
}

export default function PDFPage({ pageNumber, pdfDoc }: PDFPageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const textLayerRef = useRef<HTMLDivElement>(null);
  const drawCanvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const renderTaskRef = useRef<pdfjsLib.RenderTask | null>(null);
  const viewportRef = useRef({ width: 0, height: 0 });

  const {
    zoom,
    rotation,
    currentPage,
    activeTool,
    addAnnotation,
    annotations,
    isDrawing,
    setIsDrawing,
    currentDrawPath,
    setCurrentDrawPath,
  } = usePDFStore();

  // Redraw existing annotations on the annotation canvas
  const redrawAnnotations = useCallback(() => {
    const drawCanvas = drawCanvasRef.current;
    if (!drawCanvas) return;
    const ctx = drawCanvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);

    const pageAnnotations = annotations.filter((a) => a.pageNumber === pageNumber);

    pageAnnotations.forEach((annotation) => {
      const x = (annotation.x / 100) * drawCanvas.width;
      const y = (annotation.y / 100) * drawCanvas.height;
      const w = annotation.width ? (annotation.width / 100) * drawCanvas.width : 0;
      const h = annotation.height ? (annotation.height / 100) * drawCanvas.height : 0;

      switch (annotation.type) {
        case 'highlight':
          ctx.fillStyle = (annotation.color || '#FFEB3B') + '55';
          ctx.fillRect(x, y, w || 160, h || 20);
          ctx.strokeStyle = annotation.color || '#FFEB3B';
          ctx.lineWidth = 1;
          ctx.strokeRect(x, y, w || 160, h || 20);
          break;

        case 'underline':
          ctx.strokeStyle = annotation.color || '#2196F3';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(x, y + (h || 20));
          ctx.lineTo(x + (w || 160), y + (h || 20));
          ctx.stroke();
          break;

        case 'strikethrough':
          ctx.strokeStyle = annotation.color || '#F44336';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(x, y + (h || 20) / 2);
          ctx.lineTo(x + (w || 160), y + (h || 20) / 2);
          ctx.stroke();
          break;

        case 'text':
          ctx.fillStyle = annotation.color || '#4CAF50';
          ctx.beginPath();
          ctx.arc(x + 8, y + 8, 8, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = 'white';
          ctx.font = 'bold 10px sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('T', x + 8, y + 8);
          if (annotation.content) {
            ctx.fillStyle = '#333';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            ctx.fillText(annotation.content, x + 20, y + 2);
          }
          break;

        case 'stamp':
          ctx.fillStyle = annotation.color || '#9C27B0';
          ctx.fillRect(x, y, 70, 22);
          ctx.fillStyle = 'white';
          ctx.font = 'bold 9px sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('APPROVED', x + 35, y + 11);
          break;

        case 'draw':
          if (annotation.paths) {
            annotation.paths.forEach((path) => {
              if (path.points.length < 2) return;
              ctx.strokeStyle = path.color;
              ctx.lineWidth = path.width;
              ctx.lineCap = 'round';
              ctx.lineJoin = 'round';
              ctx.beginPath();
              ctx.moveTo(
                (path.points[0].x / 100) * drawCanvas.width,
                (path.points[0].y / 100) * drawCanvas.height
              );
              for (let i = 1; i < path.points.length; i++) {
                ctx.lineTo(
                  (path.points[i].x / 100) * drawCanvas.width,
                  (path.points[i].y / 100) * drawCanvas.height
                );
              }
              ctx.stroke();
            });
          }
          break;
      }
    });
  }, [annotations, pageNumber]);

  // Render PDF page
  const renderPage = useCallback(async () => {
    if (!pdfDoc || !canvasRef.current) return;

    try {
      const page = await pdfDoc.getPage(pageNumber);
      const viewport = page.getViewport({ scale: zoom, rotation });

      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (!context) return;

      canvas.width = viewport.width;
      canvas.height = viewport.height;
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;

      viewportRef.current = { width: viewport.width, height: viewport.height };

      if (containerRef.current) {
        containerRef.current.style.width = `${viewport.width}px`;
        containerRef.current.style.height = `${viewport.height}px`;
      }

      // Resize draw canvas
      if (drawCanvasRef.current) {
        drawCanvasRef.current.width = viewport.width;
        drawCanvasRef.current.height = viewport.height;
        drawCanvasRef.current.style.width = `${viewport.width}px`;
        drawCanvasRef.current.style.height = `${viewport.height}px`;
      }

      // Cancel previous render
      if (renderTaskRef.current) {
        renderTaskRef.current.cancel();
      }

      renderTaskRef.current = page.render({
        canvasContext: context,
        viewport: viewport,
      });

      await renderTaskRef.current.promise;
      renderTaskRef.current = null;

      // Render text layer for selection
      if (textLayerRef.current) {
        const textContent = await page.getTextContent();
        textLayerRef.current.innerHTML = '';
        textLayerRef.current.style.width = `${viewport.width}px`;
        textLayerRef.current.style.height = `${viewport.height}px`;

        const textItems = textContent.items as pdfjsLib.TextItem[];
        textItems.forEach((item) => {
          if (!item.str || !item.transform) return;
          const tx = item.transform;
          const fontSize = Math.sqrt(tx[2] * tx[2] + tx[3] * tx[3]);
          const span = document.createElement('span');
          span.textContent = item.str;
          span.style.position = 'absolute';
          span.style.left = `${tx[4]}px`;
          span.style.top = `${tx[5] - fontSize}px`;
          span.style.fontSize = `${fontSize}px`;
          span.style.fontFamily = item.fontName || 'sans-serif';
          span.style.color = 'transparent';
          span.style.whiteSpace = 'pre';
          span.style.cursor = 'text';
          span.style.userSelect = 'text';
          textLayerRef.current!.appendChild(span);
        });
      }

      // Redraw annotation layer after page render
      redrawAnnotations();
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'name' in err && (err as { name: string }).name === 'RenderingCancelledException') {
        return;
      }
      console.error('Page render error:', err);
    }
  }, [pdfDoc, pageNumber, zoom, rotation, redrawAnnotations]);

  useLayoutEffect(() => {
    renderPage();
  }, [pdfDoc, pageNumber, zoom, rotation, renderPage]);

  // Redraw annotations when they change
  useEffect(() => {
    redrawAnnotations();
  }, [annotations, redrawAnnotations]);

  // Handle mouse events for annotations
  const getRelativePos = useCallback((e: React.MouseEvent) => {
    if (!containerRef.current) return { x: 0, y: 0 };
    const rect = containerRef.current.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * 100,
      y: ((e.clientY - rect.top) / rect.height) * 100,
    };
  }, []);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (activeTool === 'hand' || activeTool === 'select') return;

      const pos = getRelativePos(e);

      if (activeTool === 'draw') {
        setIsDrawing(true);
        setCurrentDrawPath({
          points: [pos],
          color: '#FF0000',
          width: 2,
        });
        return;
      }

      const annotationType = activeTool as 'highlight' | 'text' | 'stamp' | 'underline' | 'strikethrough';
      const colorMap: Record<string, string> = {
        highlight: '#FFEB3B',
        text: '#4CAF50',
        stamp: '#9C27B0',
        underline: '#2196F3',
        strikethrough: '#F44336',
        draw: '#FF0000',
      };

      addAnnotation({
        id: `ann-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: annotationType,
        pageNumber,
        x: pos.x,
        y: pos.y,
        width: 25,
        height: 3,
        color: colorMap[annotationType] || '#FFEB3B',
        content: annotationType === 'text' ? 'Note' : undefined,
        timestamp: Date.now(),
      });
    },
    [activeTool, addAnnotation, pageNumber, getRelativePos, setIsDrawing, setCurrentDrawPath]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDrawing || activeTool !== 'draw' || !currentDrawPath) return;

      const pos = getRelativePos(e);
      const newPoints = [...currentDrawPath.points, pos];
      setCurrentDrawPath({ ...currentDrawPath, points: newPoints });

      const drawCanvas = drawCanvasRef.current;
      if (!drawCanvas) return;
      const ctx = drawCanvas.getContext('2d');
      if (!ctx) return;

      redrawAnnotations();

      if (newPoints.length >= 2) {
        ctx.strokeStyle = currentDrawPath.color;
        ctx.lineWidth = currentDrawPath.width;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.beginPath();
        ctx.moveTo(
          (newPoints[0].x / 100) * drawCanvas.width,
          (newPoints[0].y / 100) * drawCanvas.height
        );
        for (let i = 1; i < newPoints.length; i++) {
          ctx.lineTo(
            (newPoints[i].x / 100) * drawCanvas.width,
            (newPoints[i].y / 100) * drawCanvas.height
          );
        }
        ctx.stroke();
      }
    },
    [isDrawing, activeTool, currentDrawPath, getRelativePos, setCurrentDrawPath, redrawAnnotations]
  );

  const handleMouseUp = useCallback(() => {
    if (!isDrawing || !currentDrawPath || activeTool !== 'draw') return;

    if (currentDrawPath.points.length >= 2) {
      addAnnotation({
        id: `ann-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'draw',
        pageNumber,
        x: currentDrawPath.points[0].x,
        y: currentDrawPath.points[0].y,
        color: currentDrawPath.color,
        timestamp: Date.now(),
        paths: [currentDrawPath],
      });
    }

    setIsDrawing(false);
    setCurrentDrawPath(null);
  }, [isDrawing, currentDrawPath, activeTool, addAnnotation, pageNumber, setIsDrawing, setCurrentDrawPath]);

  const isActive = currentPage === pageNumber;

  const getCursorStyle = () => {
    switch (activeTool) {
      case 'hand': return 'grab';
      case 'draw': return 'crosshair';
      case 'highlight':
      case 'underline':
      case 'strikethrough':
      case 'text':
      case 'stamp':
        return 'crosshair';
      default: return 'default';
    }
  };

  return (
    <div className="flex justify-center p-4">
      <div
        ref={containerRef}
        className={`relative shadow-2xl bg-white ${isActive ? 'ring-1 ring-[#e8720c]/30' : ''}`}
        style={{ cursor: getCursorStyle() }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <canvas ref={canvasRef} className="block" />
        <div
          ref={textLayerRef}
          className="absolute top-0 left-0 overflow-hidden select-text"
          style={{ pointerEvents: activeTool === 'select' ? 'auto' : 'none' }}
        />
        <canvas
          ref={drawCanvasRef}
          className="absolute top-0 left-0 pointer-events-none"
        />
      </div>
    </div>
  );
}
