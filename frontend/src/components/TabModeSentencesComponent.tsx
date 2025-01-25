import React, { useState, useEffect, useContext } from "react";
import TTSSentenceComponent from "./TTSSentenceComponent";
import { BaseURLContext } from "../context/BaseURLContext";
import { Word } from "../App";

interface Sentence {
  sentence: string;
  id: number;
}

const TabModeSentencesComponent = ({
  selectedWord,
}: {
  selectedWord: Word;
}) => {
  const [sentences, setSentences] = useState<Sentence[]>([]);
  const baseURL = useContext(BaseURLContext);

  useEffect(() => {
    if (selectedWord) {
      const fetchSentences = async () => {
        try {
          const response = await fetch(
            `${baseURL}/api/sentences/${selectedWord.word}`
          );
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setSentences(data);
        } catch (error) {
          console.error("Could not fetch sentences:", error);
        }
      };
      fetchSentences();
    } else {
      setSentences([]);
    }
  }, [selectedWord, baseURL]);

  return (
    <div>
      <h4>
        Sentences for {selectedWord ? selectedWord.word : "Select a word"}
      </h4>
      <ul className="sentence-list">
        {sentences.map((sentenceObj) => (
          <li key={sentenceObj.id}>
            {sentenceObj.sentence}
            <TTSSentenceComponent sentence={sentenceObj.sentence} />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TabModeSentencesComponent;
