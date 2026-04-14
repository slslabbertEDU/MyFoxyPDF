'use client';

import React, { useCallback } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  RotateCcw,
  Search,
  Hand,
  MousePointer2,
  Highlighter,
  Type,
  Pencil,
  Stamp,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  FileText,
  BookOpen,
  Columns2,
  Download,
  Printer,
  FolderOpen,
  Underline,
  Strikethrough,
  MessageSquare,
} from 'lucide-react';
import { usePDFStore, ActiveTool } from './PDFStore';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function Toolbar() {
  const {
    zoom,
    zoomIn,
    zoomOut,
    setZoom,
    currentPage,
    numPages,
    goToPage,
    nextPage,
    prevPage,
    rotateClockwise,
    rotateCounterClockwise,
    viewMode,
    setViewMode,
    sidebarOpen,
    setSidebarOpen,
    rightPanelOpen,
    setRightPanelOpen,
    activeTool,
    setActiveTool,
    setIsSearchVisible,
    pdfFile,
  } = usePDFStore();

  const handlePageInput = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        const page = parseInt((e.target as HTMLInputElement).value, 10);
        if (!isNaN(page)) goToPage(page);
      }
    },
    [goToPage]
  );

  const handleZoomSelect = useCallback(
    (value: string) => {
      if (value === 'fit-width') {
        setZoom(1.25);
      } else if (value === 'fit-page') {
        setZoom(1);
      } else {
        setZoom(parseFloat(value));
      }
    },
    [setZoom]
  );

  const tools: { type: ActiveTool; icon: React.ReactNode; label: string; group: string }[] = [
    { type: 'select', icon: <MousePointer2 className="h-4 w-4" />, label: 'Select', group: 'basic' },
    { type: 'hand', icon: <Hand className="h-4 w-4" />, label: 'Hand (Pan)', group: 'basic' },
    { type: 'highlight', icon: <Highlighter className="h-4 w-4" />, label: 'Highlight', group: 'annotate' },
    { type: 'underline', icon: <Underline className="h-4 w-4" />, label: 'Underline', group: 'annotate' },
    { type: 'strikethrough', icon: <Strikethrough className="h-4 w-4" />, label: 'Strikethrough', group: 'annotate' },
    { type: 'text', icon: <Type className="h-4 w-4" />, label: 'Text Note', group: 'annotate' },
    { type: 'draw', icon: <Pencil className="h-4 w-4" />, label: 'Freehand Draw', group: 'annotate' },
    { type: 'stamp', icon: <Stamp className="h-4 w-4" />, label: 'Stamp', group: 'annotate' },
  ];

  const viewModes: { mode: typeof viewMode; icon: React.ReactNode; label: string }[] = [
    { mode: 'single', icon: <FileText className="h-4 w-4" />, label: 'Single Page' },
    { mode: 'continuous', icon: <BookOpen className="h-4 w-4" />, label: 'Continuous Scroll' },
    { mode: 'facing', icon: <Columns2 className="h-4 w-4" />, label: 'Two Pages' },
  ];

  const zoomPercent = Math.round(zoom * 100);

  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex items-center h-11 bg-[#2d2d2d] border-b border-[#1a1a1a] px-2 gap-0.5 select-none overflow-x-auto">
        {/* Left section: Toggle panels */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className={`p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer ${sidebarOpen ? 'bg-[#4a4a4a]' : ''}`}
              >
                {sidebarOpen ? (
                  <PanelLeftClose className="h-4 w-4 text-[#d4d4d4]" />
                ) : (
                  <PanelLeftOpen className="h-4 w-4 text-[#d4d4d4]" />
                )}
              </button>
            </TooltipTrigger>
            <TooltipContent>Toggle Navigation Panel</TooltipContent>
          </Tooltip>
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* File operations */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => {
                  const input = globalThis.document.createElement('input');
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
                }}
                className="p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer"
              >
                <FolderOpen className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Open File (Ctrl+O)</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer">
                <Download className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Save / Download</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => window.print()}
                className="p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer"
              >
                <Printer className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Print (Ctrl+P)</TooltipContent>
          </Tooltip>
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* Page navigation */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={prevPage}
                disabled={currentPage <= 1 || !pdfFile}
                className="p-1.5 rounded hover:bg-[#4a4a4a] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <RotateCcw className="h-3.5 w-3.5 text-[#d4d4d4] rotate-0" style={{ transform: 'scaleX(-1)' }} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Previous Page</TooltipContent>
          </Tooltip>

          <div className="flex items-center gap-1 text-[#d4d4d4] text-sm">
            <input
              type="text"
              defaultValue={currentPage}
              key={currentPage}
              className="w-10 h-6 text-center bg-[#3c3c3c] border border-[#555] rounded text-[#d4d4d4] text-xs focus:outline-none focus:border-[#e8720c]"
              onKeyDown={handlePageInput}
              onBlur={(e) => {
                const page = parseInt(e.target.value, 10);
                if (!isNaN(page)) goToPage(page);
              }}
            />
            <span className="text-[#999] text-xs">/</span>
            <span className="text-[#999] text-xs">{numPages || 0}</span>
          </div>

          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={nextPage}
                disabled={currentPage >= numPages || !pdfFile}
                className="p-1.5 rounded hover:bg-[#4a4a4a] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <RotateCw className="h-3.5 w-3.5 text-[#d4d4d4]" style={{ transform: 'scaleX(-1)' }} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Next Page</TooltipContent>
          </Tooltip>
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* Zoom controls */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={zoomOut}
                disabled={!pdfFile}
                className="p-1.5 rounded hover:bg-[#4a4a4a] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <ZoomOut className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Zoom Out (Ctrl+-)</TooltipContent>
          </Tooltip>

          <Select value={String(zoomPercent)} onValueChange={handleZoomSelect}>
            <SelectTrigger className="w-[76px] h-6 bg-[#3c3c3c] border-[#555] text-[#d4d4d4] text-xs focus:ring-0 focus:ring-offset-0 cursor-pointer">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
              <SelectItem value="50" className="focus:bg-[#4a4a4a]">50%</SelectItem>
              <SelectItem value="75" className="focus:bg-[#4a4a4a]">75%</SelectItem>
              <SelectItem value="100" className="focus:bg-[#4a4a4a]">100%</SelectItem>
              <SelectItem value="125" className="focus:bg-[#4a4a4a]">125%</SelectItem>
              <SelectItem value="150" className="focus:bg-[#4a4a4a]">150%</SelectItem>
              <SelectItem value="200" className="focus:bg-[#4a4a4a]">200%</SelectItem>
              <SelectItem value="300" className="focus:bg-[#4a4a4a]">300%</SelectItem>
              <SelectItem value="fit-width" className="focus:bg-[#4a4a4a]">Fit Width</SelectItem>
              <SelectItem value="fit-page" className="focus:bg-[#4a4a4a]">Fit Page</SelectItem>
            </SelectContent>
          </Select>

          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={zoomIn}
                disabled={!pdfFile}
                className="p-1.5 rounded hover:bg-[#4a4a4a] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <ZoomIn className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Zoom In (Ctrl++)</TooltipContent>
          </Tooltip>
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* Rotation */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={rotateCounterClockwise}
                disabled={!pdfFile}
                className="p-1.5 rounded hover:bg-[#4a4a4a] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <RotateCcw className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Rotate Left</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={rotateClockwise}
                disabled={!pdfFile}
                className="p-1.5 rounded hover:bg-[#4a4a4a] disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <RotateCw className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Rotate Right</TooltipContent>
          </Tooltip>
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* View modes */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          {viewModes.map((vm) => (
            <Tooltip key={vm.mode}>
              <TooltipTrigger asChild>
                <button
                  onClick={() => setViewMode(vm.mode)}
                  className={`p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer ${viewMode === vm.mode ? 'bg-[#4a4a4a]' : ''}`}
                >
                  <span className="text-[#d4d4d4]">{vm.icon}</span>
                </button>
              </TooltipTrigger>
              <TooltipContent>{vm.label}</TooltipContent>
            </Tooltip>
          ))}
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* Annotation tools */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          {tools.map((tool) => (
            <Tooltip key={tool.type}>
              <TooltipTrigger asChild>
                <button
                  onClick={() => setActiveTool(tool.type)}
                  className={`p-1.5 rounded cursor-pointer transition-colors ${
                    activeTool === tool.type
                      ? 'bg-[#e8720c] hover:bg-[#d4680a]'
                      : 'hover:bg-[#4a4a4a]'
                  }`}
                >
                  <span className={`${activeTool === tool.type ? 'text-white' : 'text-[#d4d4d4]'}`}>
                    {tool.icon}
                  </span>
                </button>
              </TooltipTrigger>
              <TooltipContent>{tool.label}</TooltipContent>
            </Tooltip>
          ))}
        </div>

        <div className="w-px h-6 bg-[#555] mx-1 shrink-0" />

        {/* Search & Comments */}
        <div className="flex items-center gap-0.5 mr-1 shrink-0">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setIsSearchVisible(true)}
                className="p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer"
              >
                <Search className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Find (Ctrl+F)</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setRightPanelOpen(!rightPanelOpen)}
                className={`p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer ${rightPanelOpen ? 'bg-[#4a4a4a]' : ''}`}
              >
                <MessageSquare className="h-4 w-4 text-[#d4d4d4]" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Comments Panel</TooltipContent>
          </Tooltip>
        </div>

        <div className="flex-1" />

        {/* Right panel toggle */}
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
              className={`p-1.5 rounded hover:bg-[#4a4a4a] cursor-pointer shrink-0 ${rightPanelOpen ? 'bg-[#4a4a4a]' : ''}`}
            >
              {rightPanelOpen ? (
                <PanelRightClose className="h-4 w-4 text-[#d4d4d4]" />
              ) : (
                <PanelRightOpen className="h-4 w-4 text-[#d4d4d4]" />
              )}
            </button>
          </TooltipTrigger>
          <TooltipContent>Toggle Comment Panel</TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
}
