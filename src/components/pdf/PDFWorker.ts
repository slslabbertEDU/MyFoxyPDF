'use client';

import * as pdfjsLib from 'pdfjs-dist';

let workerInitialized = false;

export function initPDFWorker() {
  if (workerInitialized) return;

  // Use the CDN version of the worker for reliability
  pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;

  workerInitialized = true;
}

export { pdfjsLib };
