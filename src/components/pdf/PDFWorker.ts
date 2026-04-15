'use client';

import * as pdfjsLib from 'pdfjs-dist';

let workerInitialized = false;

export function initPDFWorker() {
  if (workerInitialized) return;

  // Use the local copy of the worker served from /public
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

  workerInitialized = true;
}

export { pdfjsLib };
