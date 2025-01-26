import React, { useState, useRef, useContext, useEffect } from "react";
import { BaseURLContext } from "../context/BaseURLContext";

const TTSSentenceComponent = ({ sentence }: { sentence: string }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const baseURL = useContext(BaseURLContext);

  useEffect(() => {
    const currentAudio = audioRef.current;

    if (currentAudio) {
      currentAudio.onended = () => {
        setIsPlaying(false);
      };
    }

    return () => {
      if (currentAudio) {
        currentAudio.onended = null;
      }
    };
  }, []);

  const handlePlay = async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    try {
      const response = await fetch(
        `${baseURL}/api/tts?sentence=${encodeURIComponent(sentence)}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const base64Audio = data.audio_data;
      if (!base64Audio) {
        console.error("No audio data received from backend.");
        return;
      }

      const audioBlob = base64toBlob(base64Audio, "audio/wav");
      const audioURL = URL.createObjectURL(audioBlob);

      if (!audioRef.current) {
        audioRef.current = new Audio(audioURL);
      } else {
        audioRef.current.src = audioURL;
        audioRef.current.load();
      }

      setIsPlaying(true);
      await audioRef.current.play();

      audioRef.current.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioURL);
      };
    } catch (error) {
      console.error("Error fetching or playing TTS:", error);
      setIsPlaying(false);
    }
  };

  // Utility function to convert base64 string to Blob
  const base64toBlob = (base64Data: string, contentType = "audio/wav") => {
    const byteCharacters = atob(base64Data);
    const byteArrays: Uint8Array[] = [];
    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
      const slice = byteCharacters.slice(offset, offset + 512);
      const byteNumbers = new Array(slice.length);
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }
    return new Blob(byteArrays, { type: contentType });
  };

  return (
    <span>
      <button onClick={handlePlay}>{isPlaying ? "⏸️" : "▶️"}</button>
      <audio ref={audioRef} src="" preload="none" />
    </span>
  );
};

export default TTSSentenceComponent;
