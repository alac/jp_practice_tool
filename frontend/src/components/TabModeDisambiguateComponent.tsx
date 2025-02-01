import React, { useState, useEffect, useContext } from "react";
import { BaseURLContext } from "../context/BaseURLContext";
import { Word } from "../App";
import ReactMarkdown from "react-markdown";

interface DisambiguationExercise {
  question: string;
  explanation: string | null;
}

const TabModeDisambiguateComponent = ({
  selectedWord,
}: {
  selectedWord: Word;
}) => {
  const [disambiguationExercise, setDisambiguationExercise] =
    useState<DisambiguationExercise | null>(null);
  const baseURL = useContext(BaseURLContext);

  useEffect(() => {
    if (selectedWord) {
      setDisambiguationExercise(null);
      const fetchDisambiguateExercise = async () => {
        try {
          const response = await fetch(
            `${baseURL}/api/exercises/disambiguate/${selectedWord.word}`
          );
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          setDisambiguationExercise(data);
        } catch (error) {
          console.error("Could not fetch disambiguation exercise:", error);
          setDisambiguationExercise({
            question: "Error fetching exercise.",
            explanation: null,
          });
        }
      };
      fetchDisambiguateExercise();
    } else {
      setDisambiguationExercise(null);
    }
  }, [selectedWord, baseURL]);

  return (
    <div className="tab-mode-sentences" key={selectedWord.word}>
      <h4>
        Disambiguate Exercise for:{" "}
        {selectedWord ? selectedWord.word : "Select a word"}
      </h4>
      {disambiguationExercise ? (
        <div>
          <div className="markdown-content">
            <ReactMarkdown>{disambiguationExercise.question}</ReactMarkdown>
          </div>
          <details>
            <summary>Show Explanation</summary>
            <div className="markdown-content">
              <ReactMarkdown>
                {disambiguationExercise.explanation ||
                  "No explanation provided."}
              </ReactMarkdown>
            </div>
          </details>
        </div>
      ) : (
        <p>Loading exercise...</p>
      )}
    </div>
  );
};

export default TabModeDisambiguateComponent;
