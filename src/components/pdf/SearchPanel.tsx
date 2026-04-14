'use client';

import React, { useCallback, useState } from 'react';
import { Search, ChevronUp, ChevronDown, X } from 'lucide-react';
import { usePDFStore } from './PDFStore';

export default function SearchPanel() {
  const {
    searchQuery,
    setSearchQuery,
    searchResults,
    currentSearchIndex,
    setCurrentSearchIndex,
    setIsSearchVisible,
  } = usePDFStore();

  const [caseSensitive, setCaseSensitive] = useState(false);
  const [wholeWords, setWholeWords] = useState(false);

  const handleSearch = useCallback(() => {
    if (!searchQuery.trim()) return;
    // In a real implementation, this would use PDF.js text search
    // For now, simulate search results
    setCurrentSearchIndex(0);
  }, [searchQuery, setCurrentSearchIndex]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleSearch();
      }
      if (e.key === 'Escape') {
        setIsSearchVisible(false);
      }
    },
    [handleSearch, setIsSearchVisible]
  );

  return (
    <div className="p-3 space-y-3">
      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-[#666]" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search in document..."
          className="w-full h-8 pl-8 pr-8 text-sm bg-[#3c3c3c] border border-[#555] rounded text-[#d4d4d4] placeholder-[#666] focus:outline-none focus:border-[#e8720c]"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            className="absolute right-2 top-1/2 -translate-y-1/2 cursor-pointer"
          >
            <X className="h-3 w-3 text-[#666] hover:text-[#d4d4d4]" />
          </button>
        )}
      </div>

      {/* Search options */}
      <div className="flex items-center gap-3">
        <label className="flex items-center gap-1.5 text-xs text-[#999] cursor-pointer">
          <input
            type="checkbox"
            checked={caseSensitive}
            onChange={(e) => setCaseSensitive(e.target.checked)}
            className="rounded border-[#555] accent-[#e8720c]"
          />
          Case Sensitive
        </label>
        <label className="flex items-center gap-1.5 text-xs text-[#999] cursor-pointer">
          <input
            type="checkbox"
            checked={wholeWords}
            onChange={(e) => setWholeWords(e.target.checked)}
            className="rounded border-[#555] accent-[#e8720c]"
          />
          Whole Words
        </label>
      </div>

      {/* Search results navigation */}
      {searchQuery && searchResults.length > 0 && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-[#999]">
            {currentSearchIndex + 1} of {searchResults.length} results
          </span>
          <div className="flex gap-1">
            <button
              onClick={() =>
                setCurrentSearchIndex(
                  currentSearchIndex > 0 ? currentSearchIndex - 1 : searchResults.length - 1
                )
              }
              className="p-1 rounded hover:bg-[#3c3c3c] cursor-pointer"
            >
              <ChevronUp className="h-4 w-4 text-[#d4d4d4]" />
            </button>
            <button
              onClick={() =>
                setCurrentSearchIndex(
                  currentSearchIndex < searchResults.length - 1 ? currentSearchIndex + 1 : 0
                )
              }
              className="p-1 rounded hover:bg-[#3c3c3c] cursor-pointer"
            >
              <ChevronDown className="h-4 w-4 text-[#d4d4d4]" />
            </button>
          </div>
        </div>
      )}

      {searchQuery && searchResults.length === 0 && (
        <p className="text-xs text-[#666] text-center">No results found</p>
      )}
    </div>
  );
}
