'use client';

import React from 'react';
import { ChevronRight, Bookmark } from 'lucide-react';
import { usePDFStore, BookmarkItem } from './PDFStore';

function BookmarkTreeItem({ item, depth = 0 }: { item: BookmarkItem; depth?: number }) {
  const { goToPage } = usePDFStore();

  return (
    <div>
      <button
        onClick={() => goToPage(item.pageNumber)}
        className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-[#3c3c3c] text-left text-sm text-[#d4d4d4] rounded cursor-pointer"
        style={{ paddingLeft: `${12 + depth * 16}px` }}
      >
        {item.children && item.children.length > 0 ? (
          <ChevronRight className="h-3 w-3 text-[#999] shrink-0" />
        ) : (
          <span className="w-3" />
        )}
        <Bookmark className="h-3 w-3 text-[#e8720c] shrink-0" />
        <span className="truncate">{item.title}</span>
        <span className="ml-auto text-[#666] text-xs">{item.pageNumber}</span>
      </button>
      {item.children?.map((child, idx) => (
        <BookmarkTreeItem key={idx} item={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function BookmarkPanel() {
  const { bookmarks } = usePDFStore();

  if (bookmarks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-[#666] px-4">
        <Bookmark className="h-8 w-8 mb-2 opacity-40" />
        <p className="text-sm text-center">No bookmarks in this document</p>
      </div>
    );
  }

  return (
    <div className="py-1">
      {bookmarks.map((bookmark, idx) => (
        <BookmarkTreeItem key={idx} item={bookmark} />
      ))}
    </div>
  );
}
