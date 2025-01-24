import React, { useState, useRef } from 'react';

const TTSSentenceComponent = ({ sentence }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const audioRef = useRef(null);

    const handlePlay = async () => {
        if (isPlaying) {
            audioRef.current.pause();
            setIsPlaying(false);
            return;
        }

        try {
            const response = await fetch('http://localhost:5001/api/tts?sentence=${encodeURIComponent(sentence)}');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const base64Audio = data.audio_data;
            if (!base64Audio) {
                console.error("No audio data received from backend.");
                return;
            }

            const audioBlob = base64toBlob(base64Audio, 'audio/wav'); // Assuming WAV format from Azure
            const audioURL = URL.createObjectURL(audioBlob);

            if (!audioRef.current) {
                audioRef.current = new Audio(audioURL);
                audioRef.current.onended = () => {
                    setIsPlaying(false);
                    URL.revokeObjectURL(audioURL);
                    audioRef.current = null;
                };
            } else {
                audioRef.current.src = audioURL;
            }


            setIsPlaying(true);
            await audioRef.current.play();

        } catch (error) {
            console.error("Error fetching or playing TTS:", error);
            setIsPlaying(false);
        }
    };

    // Utility function to convert base64 string to Blob
    const base64toBlob = (base64Data, contentType='audio/wav') => {
        const byteCharacters = atob(base64Data);
        const byteArrays = [];
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }
        return new Blob(byteArrays, {type: contentType});
    };


    return (
        <span>
            <button onClick={handlePlay}>
                {isPlaying ? 'Pause' : 'Play'} {/* Change text or use icons */}
            </button>
            <audio ref={audioRef} src="" preload="none" /> {/* Audio element, src set dynamically */}
        </span>
    );
};

export default TTSSentenceComponent;