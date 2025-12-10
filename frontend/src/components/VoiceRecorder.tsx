"use client";

import React, { useRef, useState } from "react";
import { Mic, Square } from "lucide-react";

type Props = {
  onTranscribed: (text: string, language?: string) => void;
  onError?: (err: string) => void;
};

export default function VoiceRecorder({ onTranscribed, onError }: Props) {
  const [recording, setRecording] = useState(false);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      mediaRef.current = mr;
      chunksRef.current = [];

      mr.ondataavailable = (e: BlobEvent) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      mr.onstop = async () => {
        try {
          const blob = new Blob(chunksRef.current, { type: mediaRef.current?.mimeType || "audio/webm" });
          const fd = new FormData();
          fd.append("file", blob, "voice.webm");

          const token = localStorage.getItem("token");
          
          const res = await fetch("/api/transcribe", {
            method: "POST",
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: fd,
          });

          if (!res.ok) {
            if (res.status === 401) {
              window.location.href = "/login";
              return;
            }
            const txt = await res.text();
            onError?.(`Upload error: ${res.status} ${txt}`);
            return;
          }

          const json = await res.json();
          onTranscribed(json.text, json.language);

        } catch (err: any) {
          onError?.(err?.message || "Upload failed");
        }
      };

      mr.start();
      setRecording(true);
    } catch (err: any) {
      onError?.(err?.message || "Microphone not accessible");
    }
  }

  function stopRecording() {
    if (mediaRef.current && mediaRef.current.state !== "inactive") {
      mediaRef.current.stop();
      mediaRef.current.stream.getTracks().forEach((t) => t.stop());
    }
    setRecording(false);
  }

  return (
    <button
      onClick={() => (recording ? stopRecording() : startRecording())}
      className={`p-3.5 rounded-full shadow-lg transition-all duration-300 flex items-center justify-center group ${
        recording
          ? "bg-accent text-white ring-4 ring-accent/20 animate-pulse"
          : "bg-white text-primary-light border border-primary-light/20 hover:bg-primary hover:text-white hover:shadow-organic hover:-translate-y-0.5"
      }`}
      title={recording ? "Stop Recording" : "Speak your query"}
    >
      {recording ? (
        <Square className="w-5 h-5 fill-current" />
      ) : (
        <Mic className="w-5 h-5" />
      )}
    </button>
  );
}