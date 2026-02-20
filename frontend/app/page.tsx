'use client';
import { useState, useEffect, useRef } from 'react';

export default function Home() {
  const [prefix, setPrefix] = useState('');
  const [story, setStory] = useState('');
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef(null);
  const storyRef = useRef(null);

  useEffect(() => {
    setTimeout(() => setVisible(true), 100);
  }, []);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  function stop() {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setLoading(false);
    setStreaming(false);
  }

  async function generate() {
    if (!prefix.trim()) return;
    setLoading(true);
    setStreaming(true);
    setStory('');

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${BACKEND_URL}/generate-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prefix, max_length: 500 }),
        signal: controller.signal,
      });

      if (!res.ok) throw new Error('Server error');

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');

      setLoading(false);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setStory(prev => prev + chunk);
        // Auto-scroll
        if (storyRef.current) {
          storyRef.current.scrollTop = storyRef.current.scrollHeight;
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setStory('خطا: بیک اینڈ سے جڑنے میں ناکامی');
      }
    }

    abortRef.current = null;
    setLoading(false);
    setStreaming(false);
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
          background: #0d0a07;
          min-height: 100vh;
          overflow-x: hidden;
        }

        .bg {
          position: fixed;
          inset: 0;
          background: 
            radial-gradient(ellipse at 20% 20%, rgba(180, 120, 40, 0.08) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 80%, rgba(120, 60, 20, 0.1) 0%, transparent 60%),
            radial-gradient(ellipse at 50% 50%, rgba(10, 6, 2, 0.9) 0%, transparent 100%);
          z-index: 0;
        }

        .noise {
          position: fixed;
          inset: 0;
          opacity: 0.03;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
          z-index: 0;
        }

        .border-deco {
          position: fixed;
          inset: 16px;
          border: 1px solid rgba(180, 130, 50, 0.15);
          pointer-events: none;
          z-index: 1;
        }

        .border-deco::before {
          content: '';
          position: absolute;
          inset: 6px;
          border: 1px solid rgba(180, 130, 50, 0.07);
        }

        .corner {
          position: absolute;
          width: 24px;
          height: 24px;
          border-color: rgba(200, 150, 60, 0.5);
          border-style: solid;
        }
        .corner.tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
        .corner.tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
        .corner.bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }
        .corner.br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

        .container {
          position: relative;
          z-index: 2;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 60px 20px;
          opacity: 0;
          transform: translateY(20px);
          transition: opacity 0.8s ease, transform 0.8s ease;
        }

        .container.visible {
          opacity: 1;
          transform: translateY(0);
        }

        .header {
          text-align: center;
          margin-bottom: 50px;
        }

        .subtitle {
          font-family: 'Amiri', serif;
          color: rgba(200, 150, 60, 0.7);
          font-size: 13px;
          letter-spacing: 4px;
          text-transform: uppercase;
          margin-bottom: 16px;
        }

        .title {
          font-family: 'Noto Nastaliq Urdu', 'Amiri', serif;
          font-size: clamp(36px, 6vw, 64px);
          color: #e8d5a3;
          direction: rtl;
          line-height: 1.4;
          text-shadow: 0 0 60px rgba(200, 150, 60, 0.2);
          margin-bottom: 8px;
        }

        .divider {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 20px;
          justify-content: center;
        }

        .divider-line {
          width: 80px;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(200, 150, 60, 0.5), transparent);
        }

        .divider-diamond {
          width: 6px;
          height: 6px;
          background: rgba(200, 150, 60, 0.6);
          transform: rotate(45deg);
        }

        .card {
          width: 100%;
          max-width: 720px;
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(200, 150, 60, 0.12);
          border-radius: 2px;
          padding: 40px;
          backdrop-filter: blur(10px);
          box-shadow: 0 0 80px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
        }

        .input-label {
          font-family: 'Amiri', serif;
          color: rgba(200, 150, 60, 0.6);
          font-size: 11px;
          letter-spacing: 3px;
          text-transform: uppercase;
          margin-bottom: 12px;
          display: block;
          text-align: right;
          direction: rtl;
        }

        textarea {
          width: 100%;
          background: rgba(0,0,0,0.3);
          border: 1px solid rgba(200, 150, 60, 0.15);
          border-radius: 2px;
          padding: 16px 20px;
          color: #e8d5a3;
          font-family: 'Noto Nastaliq Urdu', 'Amiri', serif;
          font-size: 18px;
          direction: rtl;
          resize: none;
          outline: none;
          line-height: 2;
          transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        textarea:focus {
          border-color: rgba(200, 150, 60, 0.4);
          box-shadow: 0 0 20px rgba(200, 150, 60, 0.05);
        }

        textarea::placeholder { color: rgba(200, 150, 60, 0.25); }

        .btn-wrapper {
          display: flex;
          justify-content: center;
          gap: 16px;
          margin-top: 24px;
        }

        button {
          background: transparent;
          border: 1px solid rgba(200, 150, 60, 0.4);
          color: #e8d5a3;
          font-family: 'Noto Nastaliq Urdu', 'Amiri', serif;
          font-size: 17px;
          padding: 12px 48px;
          cursor: pointer;
          direction: rtl;
          letter-spacing: 1px;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        button::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, rgba(200,150,60,0.1), transparent);
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        button:hover::before { opacity: 1; }
        button:hover {
          border-color: rgba(200, 150, 60, 0.7);
          box-shadow: 0 0 30px rgba(200, 150, 60, 0.1);
        }

        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        button.stop-btn {
          border-color: rgba(200, 80, 60, 0.4);
          color: rgba(230, 160, 140, 0.9);
          padding: 12px 28px;
        }

        button.stop-btn:hover {
          border-color: rgba(200, 80, 60, 0.8);
          box-shadow: 0 0 30px rgba(200, 80, 60, 0.1);
        }

        .loader {
          display: flex;
          justify-content: center;
          gap: 8px;
          margin-top: 32px;
        }

        .dot {
          width: 6px;
          height: 6px;
          background: rgba(200, 150, 60, 0.6);
          border-radius: 50%;
          animation: pulse 1.4s ease-in-out infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes pulse {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
          40% { transform: scale(1); opacity: 1; }
        }

        .story-container {
          margin-top: 40px;
          width: 100%;
          max-width: 720px;
          animation: fadeIn 0.6s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .story-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
          justify-content: flex-end;
        }

        .story-label {
          font-family: 'Amiri', serif;
          color: rgba(200, 150, 60, 0.5);
          font-size: 11px;
          letter-spacing: 3px;
          text-transform: uppercase;
        }

        .streaming-badge {
          font-family: 'Amiri', serif;
          font-size: 10px;
          letter-spacing: 2px;
          text-transform: uppercase;
          color: rgba(200, 150, 60, 0.7);
          border: 1px solid rgba(200, 150, 60, 0.3);
          padding: 2px 8px;
          animation: blink 1.2s ease-in-out infinite;
        }

        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }

        .story-text {
          background: rgba(0,0,0,0.2);
          border: 1px solid rgba(200, 150, 60, 0.08);
          border-radius: 2px;
          padding: 32px 36px;
          color: #d4bc8a;
          font-family: 'Noto Nastaliq Urdu', 'Amiri', serif;
          font-size: 19px;
          direction: rtl;
          line-height: 2.4;
          white-space: pre-wrap;
          text-align: right;
          max-height: 520px;
          overflow-y: auto;
          scroll-behavior: smooth;
        }

        .story-text::-webkit-scrollbar {
          width: 4px;
        }
        .story-text::-webkit-scrollbar-track {
          background: transparent;
        }
        .story-text::-webkit-scrollbar-thumb {
          background: rgba(200, 150, 60, 0.2);
          border-radius: 2px;
        }

        .cursor {
          display: inline-block;
          width: 2px;
          height: 1.2em;
          background: rgba(200, 150, 60, 0.7);
          margin-right: 2px;
          vertical-align: middle;
          animation: blink 0.8s step-end infinite;
        }
      `}</style>

      <div className="bg" />
      <div className="noise" />
      <div className="border-deco">
        <div className="corner tl" />
        <div className="corner tr" />
        <div className="corner bl" />
        <div className="corner br" />
      </div>

      <div className={`container ${visible ? 'visible' : ''}`}>
        <div className="header">
          <p className="subtitle">Urdu Story Generator</p>
          <h1 className="title">اردو کہانی ساز</h1>
          <div className="divider">
            <div className="divider-line" />
            <div className="divider-diamond" />
            <div className="divider-line" />
          </div>
        </div>

        <div className="card">
          <label className="input-label">کہانی کا آغاز لکھیں</label>
          <textarea
            rows={3}
            value={prefix}
            onChange={e => setPrefix(e.target.value)}
            placeholder="یہاں اپنی کہانی شروع کریں..."
            disabled={streaming}
          />
          <div className="btn-wrapper">
            <button onClick={generate} disabled={loading || streaming}>
              {loading ? 'جڑ رہے ہیں...' : '✦ کہانی بنائیں ✦'}
            </button>
            {streaming && (
              <button className="stop-btn" onClick={stop}>
                ✕ روکیں
              </button>
            )}
          </div>
        </div>

        {loading && (
          <div className="loader">
            <div className="dot" />
            <div className="dot" />
            <div className="dot" />
          </div>
        )}

        {story && (
          <div className="story-container">
            <div className="story-header">
              <div className="divider-line" />
              {streaming && <span className="streaming-badge">Live</span>}
              <span className="story-label">Generated Story</span>
            </div>
            <div className="story-text" ref={storyRef}>
              {story}
              {streaming && <span className="cursor" />}
            </div>
          </div>
        )}
      </div>
    </>
  );
}