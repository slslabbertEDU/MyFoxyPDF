'use client';

import React from 'react';
import MenuBar from './MenuBar';
import TabBar from './TabBar';
import Toolbar from './Toolbar';
import Sidebar from './Sidebar';
import PDFViewer from './PDFViewer';
import RightPanel from './RightPanel';
import StatusBar from './StatusBar';
import SearchBar from './SearchBar';

export default function PDFApp() {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#1e1e1e]">
      {/* Menu bar */}
      <MenuBar />

      {/* Tab bar */}
      <TabBar />

      {/* Toolbar */}
      <Toolbar />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left sidebar */}
        <Sidebar />

        {/* PDF Viewer with search overlay */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          <SearchBar />
          <PDFViewer />
        </div>

        {/* Right panel */}
        <RightPanel />
      </div>

      {/* Status bar */}
      <StatusBar />
    </div>
  );
}
