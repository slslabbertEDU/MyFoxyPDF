'use client';

import React, { useCallback } from 'react';
import {
  Download,
  Printer,
  RotateCw,
  RotateCcw,
  Search,
  BookOpen,
  PanelLeft,
  PanelRight,
  Moon,
  Sun,
  FileText,
  FolderOpen,
  Save,
  Share2,
  Clipboard,
  Undo2,
  Redo2,
  Scissors,
  Copy,
  CheckSquare,
  MousePointer2,
  Hand,
  Highlighter,
  Type,
  Pencil,
  Stamp,
  Underline,
  Strikethrough,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { usePDFStore } from './PDFStore';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuShortcut,
} from '@/components/ui/dropdown-menu';

export default function MenuBar() {
  const {
    setSidebarOpen,
    sidebarOpen,
    setRightPanelOpen,
    rightPanelOpen,
    zoomIn,
    zoomOut,
    rotateClockwise,
    rotateCounterClockwise,
    setViewMode,
    viewMode,
    setIsSearchVisible,
    themeMode,
    setThemeMode,
    activeTool,
    setActiveTool,
  } = usePDFStore();

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

  const handlePrint = useCallback(() => {
    window.print();
  }, []);

  const toggleTheme = useCallback(() => {
    const newMode = themeMode === 'light' ? 'dark' : 'light';
    setThemeMode(newMode);
    document.documentElement.classList.toggle('dark', newMode === 'dark');
  }, [themeMode, setThemeMode]);

  return (
    <div className="flex items-center h-7 bg-[#3c3c3c] border-b border-[#2a2a2a] px-1 text-[12px] text-[#d4d4d4] select-none">
      <DropdownMenu>
        <DropdownMenuTrigger className="px-2.5 py-0.5 hover:bg-[#4a4a4a] rounded-sm outline-none cursor-pointer">
          File
        </DropdownMenuTrigger>
        <DropdownMenuContent className="min-w-[220px] bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
          <DropdownMenuItem onClick={handleOpenFile} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <FolderOpen className="mr-2 h-4 w-4" /> Open...
            <DropdownMenuShortcut>Ctrl+O</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Save className="mr-2 h-4 w-4" /> Save
            <DropdownMenuShortcut>Ctrl+S</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Download className="mr-2 h-4 w-4" /> Save As...
            <DropdownMenuShortcut>Ctrl+Shift+S</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem onClick={handlePrint} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Printer className="mr-2 h-4 w-4" /> Print...
            <DropdownMenuShortcut>Ctrl+P</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Share2 className="mr-2 h-4 w-4" /> Share
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <FileText className="mr-2 h-4 w-4" /> Properties
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-2.5 py-0.5 hover:bg-[#4a4a4a] rounded-sm outline-none cursor-pointer">
          Edit
        </DropdownMenuTrigger>
        <DropdownMenuContent className="min-w-[220px] bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Undo2 className="mr-2 h-4 w-4" /> Undo
            <DropdownMenuShortcut>Ctrl+Z</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Redo2 className="mr-2 h-4 w-4" /> Redo
            <DropdownMenuShortcut>Ctrl+Y</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Scissors className="mr-2 h-4 w-4" /> Cut
            <DropdownMenuShortcut>Ctrl+X</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Copy className="mr-2 h-4 w-4" /> Copy
            <DropdownMenuShortcut>Ctrl+C</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Clipboard className="mr-2 h-4 w-4" /> Paste
            <DropdownMenuShortcut>Ctrl+V</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <CheckSquare className="mr-2 h-4 w-4" /> Select All
            <DropdownMenuShortcut>Ctrl+A</DropdownMenuShortcut>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-2.5 py-0.5 hover:bg-[#4a4a4a] rounded-sm outline-none cursor-pointer">
          View
        </DropdownMenuTrigger>
        <DropdownMenuContent className="min-w-[240px] bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
          <DropdownMenuItem onClick={() => setSidebarOpen(!sidebarOpen)} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <PanelLeft className="mr-2 h-4 w-4" /> {sidebarOpen ? 'Hide' : 'Show'} Navigation Panel
            <DropdownMenuShortcut>F4</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setRightPanelOpen(!rightPanelOpen)} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <PanelRight className="mr-2 h-4 w-4" /> {rightPanelOpen ? 'Hide' : 'Show'} Comment Panel
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem onClick={() => setViewMode('single')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <FileText className="mr-2 h-4 w-4" /> Single Page {viewMode === 'single' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setViewMode('continuous')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <BookOpen className="mr-2 h-4 w-4" /> Continuous {viewMode === 'continuous' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setViewMode('facing')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <BookOpen className="mr-2 h-4 w-4" /> Facing {viewMode === 'facing' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem onClick={rotateClockwise} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <RotateCw className="mr-2 h-4 w-4" /> Rotate Clockwise
            <DropdownMenuShortcut>Ctrl+Shift+R</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={rotateCounterClockwise} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <RotateCcw className="mr-2 h-4 w-4" /> Rotate Counter-clockwise
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-2.5 py-0.5 hover:bg-[#4a4a4a] rounded-sm outline-none cursor-pointer">
          Annotate
        </DropdownMenuTrigger>
        <DropdownMenuContent className="min-w-[220px] bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
          <DropdownMenuItem onClick={() => setActiveTool('select')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <MousePointer2 className="mr-2 h-4 w-4" /> Select Tool {activeTool === 'select' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setActiveTool('hand')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Hand className="mr-2 h-4 w-4" /> Hand Tool {activeTool === 'hand' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem onClick={() => setActiveTool('highlight')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Highlighter className="mr-2 h-4 w-4" /> Highlight {activeTool === 'highlight' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setActiveTool('underline')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Underline className="mr-2 h-4 w-4" /> Underline {activeTool === 'underline' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setActiveTool('strikethrough')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Strikethrough className="mr-2 h-4 w-4" /> Strikethrough {activeTool === 'strikethrough' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuSeparator className="bg-[#555]" />
          <DropdownMenuItem onClick={() => setActiveTool('text')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Type className="mr-2 h-4 w-4" /> Text Note {activeTool === 'text' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setActiveTool('draw')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Pencil className="mr-2 h-4 w-4" /> Freehand Draw {activeTool === 'draw' && '✓'}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setActiveTool('stamp')} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Stamp className="mr-2 h-4 w-4" /> Stamp {activeTool === 'stamp' && '✓'}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-2.5 py-0.5 hover:bg-[#4a4a4a] rounded-sm outline-none cursor-pointer">
          Tools
        </DropdownMenuTrigger>
        <DropdownMenuContent className="min-w-[220px] bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
          <DropdownMenuItem onClick={() => setIsSearchVisible(true)} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <Search className="mr-2 h-4 w-4" /> Search
            <DropdownMenuShortcut>Ctrl+F</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={zoomIn} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <ZoomIn className="mr-2 h-4 w-4" /> Zoom In
            <DropdownMenuShortcut>Ctrl+=</DropdownMenuShortcut>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={zoomOut} className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            <ZoomOut className="mr-2 h-4 w-4" /> Zoom Out
            <DropdownMenuShortcut>Ctrl+-</DropdownMenuShortcut>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-2.5 py-0.5 hover:bg-[#4a4a4a] rounded-sm outline-none cursor-pointer">
          Help
        </DropdownMenuTrigger>
        <DropdownMenuContent className="min-w-[180px] bg-[#3c3c3c] border-[#555] text-[#d4d4d4]">
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            About Foxit PDF Clone
          </DropdownMenuItem>
          <DropdownMenuItem className="hover:bg-[#4a4a4a] focus:bg-[#4a4a4a] cursor-pointer">
            Keyboard Shortcuts
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <div className="flex-1" />

      <button
        onClick={toggleTheme}
        className="p-1 mr-1 hover:bg-[#4a4a4a] rounded-sm cursor-pointer"
        title={themeMode === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
      >
        {themeMode === 'light' ? (
          <Moon className="h-3.5 w-3.5 text-[#d4d4d4]" />
        ) : (
          <Sun className="h-3.5 w-3.5 text-[#d4d4d4]" />
        )}
      </button>
    </div>
  );
}
