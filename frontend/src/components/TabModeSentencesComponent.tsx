import React, { useState, useEffect, useContext } from "react";
import TTSSentenceComponent from "./TTSSentenceComponent";
import { BaseURLContext } from "../context/BaseURLContext";
import { Word } from "../App";

interface Sentence {
  filename: string;
  line_number: number;
  sentences: string[];
  example_line: number;
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
            `${baseURL}/api/examples/${selectedWord.word}`
          );
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          const shuffledData = [...data].sort(() => Math.random() - 0.5);
          setSentences(shuffledData);
        } catch (error) {
          console.error("Could not fetch examples:", error);
        }
      };
      fetchSentences();
    } else {
      setSentences([]);
    }
  }, [selectedWord, baseURL]);

  return (
    <div className="tab-mode-sentences">
      <h4>
        Sentences for: {selectedWord ? selectedWord.word : "Select a word"}
      </h4>
      <ul className="sentence-list">
        {sentences.map((example, index) => (
          <li key={index} className="example-block">
            <h5 className="example-title">
              File: {example.filename}, Line: {example.line_number}
            </h5>
            <div className="sentences-container">
              {example.sentences.map((sentence, sentenceIndex) => (
                <div
                  key={sentenceIndex}
                  className={`sentence-item ${
                    sentenceIndex === example.example_line
                      ? "example-sentence"
                      : ""
                  }`}
                >
                  <TTSSentenceComponent sentence={sentence} />
                  <span className="sentence-text">{sentence}</span>
                </div>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TabModeSentencesComponent;
