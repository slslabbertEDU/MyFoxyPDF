'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Search,
  ChevronUp,
  ChevronDown,
  X,
  CaseSensitive,
  WholeWord,
} from 'lucide-react';
import { usePDFStore } from './PDFStore';
import { pdfjsLib, initPDFWorker } from './PDFWorker';

export default function SearchBar() {
  const {
    isSearchVisible,
    setIsSearchVisible,
    searchQuery,
    setSearchQuery,
    searchResults,
    setSearchResults,
    currentSearchIndex,
    setCurrentSearchIndex,
    document,
    goToPage,
  } = usePDFStore();

  const [caseSensitive, setCaseSensitive] = useState(false);
  const [wholeWords, setWholeWords] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isSearchVisible && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isSearchVisible]);

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim() || !document) return;

    setIsSearching(true);
    try {
      initPDFWorker();
      const arrayBuffer = await document.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const results: number[] = [];

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items
          .map((item) => ('str' in item ? item.str : ''))
          .join(' ');

        const query = caseSensitive ? searchQuery : searchQuery.toLowerCase();
        const text = caseSensitive ? pageText : pageText.toLowerCase();

        if (wholeWords) {
          const regex = new RegExp(`\\b${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, caseSensitive ? '' : 'i');
          if (regex.test(text)) results.push(i);
        } else {
          if (text.includes(query)) results.push(i);
        }
      }

      setSearchResults(results);
      if (results.length > 0) {
        setCurrentSearchIndex(0);
        goToPage(results[0]);
      }
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery, document, caseSensitive, wholeWords, setSearchResults, setCurrentSearchIndex, goToPage]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        if (searchResults.length > 0) {
          const nextIndex = (currentSearchIndex + 1) % searchResults.length;
          setCurrentSearchIndex(nextIndex);
          goToPage(searchResults[nextIndex]);
        } else {
          handleSearch();
        }
      }
      if (e.key === 'Escape') {
        setIsSearchVisible(false);
      }
    },
    [searchResults, currentSearchIndex, setCurrentSearchIndex, goToPage, handleSearch, setIsSearchVisible]
  );

  if (!isSearchVisible) return null;

  return (
    <div className="absolute top-3 right-4 z-50 flex items-center gap-2 bg-[#333] border border-[#555] rounded-lg shadow-2xl p-2">
      <Search className="h-4 w-4 text-[#999] shrink-0" />
      <input
        ref={inputRef}
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Find in document..."
        className="w-52 h-7 px-2 text-sm bg-[#2d2d2d] border border-[#555] rounded text-[#d4d4d4] placeholder-[#666] focus:outline-none focus:border-[#e8720c]"
      />
      <button
        onClick={() => setCaseSensitive(!caseSensitive)}
        className={`p-1 rounded cursor-pointer transition-colors ${caseSensitive ? 'bg-[#e8720c] text-white' : 'text-[#999] hover:text-[#d4d4d4]'}`}
        title="Case Sensitive"
      >
        <CaseSensitive className="h-4 w-4" />
      </button>
      <button
        onClick={() => setWholeWords(!wholeWords)}
        className={`p-1 rounded cursor-pointer transition-colors ${wholeWords ? 'bg-[#e8720c] text-white' : 'text-[#999] hover:text-[#d4d4d4]'}`}
        title="Whole Words"
      >
        <WholeWord className="h-4 w-4" />
      </button>
      {isSearching && (
        <div className="w-4 h-4 border-2 border-[#e8720c] border-t-transparent rounded-full animate-spin" />
      )}
      {searchResults.length > 0 && (
        <span className="text-xs text-[#999] whitespace-nowrap min-w-[50px] text-center">
          {currentSearchIndex + 1}/{searchResults.length}
        </span>
      )}
      {searchResults.length === 0 && searchQuery && !isSearching && (
        <span className="text-xs text-[#e55] whitespace-nowrap">0/0</span>
      )}
      {searchResults.length > 0 && (
        <>
          <button
            onClick={() => {
              const prev = currentSearchIndex > 0 ? currentSearchIndex - 1 : searchResults.length - 1;
              setCurrentSearchIndex(prev);
              goToPage(searchResults[prev]);
            }}
            className="p-1 rounded hover:bg-[#4a4a4a] cursor-pointer"
          >
            <ChevronUp className="h-4 w-4 text-[#d4d4d4]" />
          </button>
          <button
            onClick={() => {
              const next = currentSearchIndex < searchResults.length - 1 ? currentSearchIndex + 1 : 0;
              setCurrentSearchIndex(next);
              goToPage(searchResults[next]);
            }}
            className="p-1 rounded hover:bg-[#4a4a4a] cursor-pointer"
          >
            <ChevronDown className="h-4 w-4 text-[#d4d4d4]" />
          </button>
        </>
      )}
      <button onClick={() => setIsSearchVisible(false)} className="p-1 rounded hover:bg-[#4a4a4a] cursor-pointer">
        <X className="h-4 w-4 text-[#999]" />
      </button>
    </div>
  );
}
