'use client';

import { create } from 'zustand';

export type SidebarTab = 'thumbnails' | 'bookmarks' | 'search' | 'annotations';
export type AnnotationType = 'highlight' | 'text' | 'draw' | 'stamp' | 'underline' | 'strikethrough' | 'none';
export type ViewMode = 'single' | 'continuous' | 'facing' | 'facing-continuous';
export type ThemeMode = 'light' | 'dark';
export type ActiveTool = 'select' | 'hand' | 'highlight' | 'text' | 'draw' | 'stamp' | 'underline' | 'strikethrough';

export interface Annotation {
  id: string;
  type: AnnotationType;
  pageNumber: number;
  x: number;
  y: number;
  width?: number;
  height?: number;
  content?: string;
  color?: string;
  timestamp: number;
  paths?: DrawPath[];
}

export interface DrawPath {
  points: { x: number; y: number }[];
  color: string;
  width: number;
}

export interface BookmarkItem {
  title: string;
  pageNumber: number;
  children?: BookmarkItem[];
}

export interface PDFTab {
  id: string;
  name: string;
  document: File | null;
}

export interface PDFState {
  // Document
  document: File | null;
  documentName: string;
  numPages: number;
  currentPage: number;
  isLoading: boolean;
  error: string | null;

  // View
  zoom: number;
  rotation: number;
  viewMode: ViewMode;
  themeMode: ThemeMode;
  isFullscreen: boolean;

  // Sidebar
  sidebarOpen: boolean;
  sidebarTab: SidebarTab;
  sidebarWidth: number;

  // Right panel
  rightPanelOpen: boolean;
  rightPanelWidth: number;

  // Tabs
  tabs: PDFTab[];
  activeTabId: string | null;

  // Annotations
  annotations: Annotation[];
  activeAnnotationType: AnnotationType;
  activeTool: ActiveTool;
  selectedAnnotation: string | null;
  isDrawing: boolean;
  currentDrawPath: DrawPath | null;

  // Search
  searchQuery: string;
  searchResults: number[];
  currentSearchIndex: number;
  isSearchVisible: boolean;

  // Bookmarks
  bookmarks: BookmarkItem[];

  // Actions
  setDocument: (file: File | null) => void;
  setDocumentName: (name: string) => void;
  setNumPages: (num: number) => void;
  setCurrentPage: (page: number) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setZoom: (zoom: number) => void;
  setRotation: (rotation: number) => void;
  setViewMode: (mode: ViewMode) => void;
  setThemeMode: (mode: ThemeMode) => void;
  setIsFullscreen: (fullscreen: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarTab: (tab: SidebarTab) => void;
  setSidebarWidth: (width: number) => void;
  setRightPanelOpen: (open: boolean) => void;
  setRightPanelWidth: (width: number) => void;
  addTab: (tab: PDFTab) => void;
  removeTab: (id: string) => void;
  setActiveTab: (id: string | null) => void;
  addAnnotation: (annotation: Annotation) => void;
  removeAnnotation: (id: string) => void;
  updateAnnotation: (id: string, updates: Partial<Annotation>) => void;
  setActiveAnnotationType: (type: AnnotationType) => void;
  setActiveTool: (tool: ActiveTool) => void;
  setSelectedAnnotation: (id: string | null) => void;
  setIsDrawing: (drawing: boolean) => void;
  setCurrentDrawPath: (path: DrawPath | null) => void;
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: number[]) => void;
  setCurrentSearchIndex: (index: number) => void;
  setIsSearchVisible: (visible: boolean) => void;
  setBookmarks: (bookmarks: BookmarkItem[]) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  fitToWidth: () => void;
  fitToPage: () => void;
  goToPage: (page: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  rotateClockwise: () => void;
  rotateCounterClockwise: () => void;
  reset: () => void;
}

const ZOOM_LEVELS = [0.25, 0.33, 0.5, 0.67, 0.75, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5];

const initialState = {
  document: null,
  documentName: '',
  numPages: 0,
  currentPage: 1,
  isLoading: false,
  error: null,
  zoom: 1,
  rotation: 0,
  viewMode: 'continuous' as ViewMode,
  themeMode: 'dark' as ThemeMode,
  isFullscreen: false,
  sidebarOpen: true,
  sidebarTab: 'thumbnails' as SidebarTab,
  sidebarWidth: 220,
  rightPanelOpen: false,
  rightPanelWidth: 280,
  tabs: [] as PDFTab[],
  activeTabId: null as string | null,
  annotations: [],
  activeAnnotationType: 'none' as AnnotationType,
  activeTool: 'select' as ActiveTool,
  selectedAnnotation: null,
  isDrawing: false,
  currentDrawPath: null,
  searchQuery: '',
  searchResults: [],
  currentSearchIndex: -1,
  isSearchVisible: false,
  bookmarks: [],
};

export const usePDFStore = create<PDFState>((set, get) => ({
  ...initialState,

  setDocument: (file) => set({ document: file }),
  setDocumentName: (name) => set({ documentName: name }),
  setNumPages: (numPages) => set({ numPages }),
  setCurrentPage: (currentPage) => set({ currentPage }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setZoom: (zoom) => set({ zoom: Math.max(0.1, Math.min(10, zoom)) }),
  setRotation: (rotation) => set({ rotation: ((rotation % 360) + 360) % 360 }),
  setViewMode: (viewMode) => set({ viewMode }),
  setThemeMode: (themeMode) => set({ themeMode }),
  setIsFullscreen: (isFullscreen) => set({ isFullscreen }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setSidebarTab: (sidebarTab) => set({ sidebarTab }),
  setSidebarWidth: (sidebarWidth) => set({ sidebarWidth }),
  setRightPanelOpen: (rightPanelOpen) => set({ rightPanelOpen }),
  setRightPanelWidth: (rightPanelWidth) => set({ rightPanelWidth }),
  addTab: (tab) => set((state) => ({ tabs: [...state.tabs, tab], activeTabId: tab.id })),
  removeTab: (id) => set((state) => {
    const newTabs = state.tabs.filter((t) => t.id !== id);
    return {
      tabs: newTabs,
      activeTabId: state.activeTabId === id ? (newTabs.length > 0 ? newTabs[newTabs.length - 1].id : null) : state.activeTabId,
    };
  }),
  setActiveTab: (id) => set({ activeTabId: id }),
  addAnnotation: (annotation) =>
    set((state) => ({ annotations: [...state.annotations, annotation] })),
  removeAnnotation: (id) =>
    set((state) => ({ annotations: state.annotations.filter((a) => a.id !== id) })),
  updateAnnotation: (id, updates) =>
    set((state) => ({
      annotations: state.annotations.map((a) =>
        a.id === id ? { ...a, ...updates } : a
      ),
    })),
  setActiveAnnotationType: (activeAnnotationType) => set({ activeAnnotationType }),
  setActiveTool: (activeTool) => set({ activeTool }),
  setSelectedAnnotation: (selectedAnnotation) => set({ selectedAnnotation }),
  setIsDrawing: (isDrawing) => set({ isDrawing }),
  setCurrentDrawPath: (currentDrawPath) => set({ currentDrawPath }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSearchResults: (searchResults) => set({ searchResults }),
  setCurrentSearchIndex: (currentSearchIndex) => set({ currentSearchIndex }),
  setIsSearchVisible: (isSearchVisible) => set({ isSearchVisible }),
  setBookmarks: (bookmarks) => set({ bookmarks }),

  zoomIn: () => {
    const { zoom } = get();
    const nextZoom = ZOOM_LEVELS.find((z) => z > zoom + 0.01);
    set({ zoom: nextZoom || zoom * 1.2 });
  },
  zoomOut: () => {
    const { zoom } = get();
    const prevZoom = [...ZOOM_LEVELS].reverse().find((z) => z < zoom - 0.01);
    set({ zoom: prevZoom || zoom / 1.2 });
  },
  fitToWidth: () => set({ zoom: 1.25 }),
  fitToPage: () => set({ zoom: 1 }),

  goToPage: (page) => {
    const { numPages } = get();
    if (page >= 1 && page <= numPages) {
      set({ currentPage: page });
    }
  },
  nextPage: () => {
    const { currentPage, numPages } = get();
    if (currentPage < numPages) set({ currentPage: currentPage + 1 });
  },
  prevPage: () => {
    const { currentPage } = get();
    if (currentPage > 1) set({ currentPage: currentPage - 1 });
  },
  rotateClockwise: () => {
    const { rotation } = get();
    set({ rotation: (rotation + 90) % 360 });
  },
  rotateCounterClockwise: () => {
    const { rotation } = get();
    set({ rotation: (rotation - 90 + 360) % 360 });
  },
  reset: () => set(initialState),
}));
