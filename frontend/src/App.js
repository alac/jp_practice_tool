import React, { useState, useEffect } from "react";
import "./App.css";
import { BaseURLContext, BASE_URL } from "./contexts/BaseURLContext";

function App() {
  const [words, setWords] = useState([]);
  const [selectedWord, setSelectedWord] = useState(null);
  const [loadingWords, setLoadingWords] = useState(false);

  // Modal Visibility States
  const [isRecentModalOpen, setIsRecentModalOpen] = useState(false);
  const [isDifficultModalOpen, setIsDifficultModalOpen] = useState(false);
  const [isExactModalOpen, setIsExactModalOpen] = useState(false);

  // Modal Input States
  const [recentDaysInput, setRecentDaysInput] = useState("7");
  const [recentLimitInput, setRecentLimitInput] = useState("10");
  const [difficultLimitInput, setDifficultLimitInput] = useState("100");
  const [difficultRepsInput, setDifficultRepsInput] = useState("30");
  const [difficultEaseInput, setDifficultEaseInput] = useState("1.4");
  const [exactSearchInput, setExactSearchInput] = useState("");
  const [exactLimitInput, setExactLimitInput] = useState("100");

  const fetchWords = async () => {
    setLoadingWords(true);
    try {
      const response = await fetch(`${BASE_URL}/api/words`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setWords(data);
    } catch (error) {
      console.error("Could not fetch words:", error);
    } finally {
      setLoadingWords(false);
    }
  };

  useEffect(() => {
    fetchWords();
  }, []);

  const handleWordSelect = (word) => {
    setSelectedWord(word);
  };

  const handleTabChange = (tabName) => {
    setCurrentTab(tabName);
  };

  // Modal Open/Close Handlers
  const openRecentModal = () => setIsRecentModalOpen(true);
  const closeRecentModal = () => setIsRecentModalOpen(false);
  const openDifficultModal = () => setIsDifficultModalOpen(true);
  const closeDifficultModal = () => setIsDifficultModalOpen(false);
  const openExactModal = () => setIsExactModalOpen(true);
  const closeExactModal = () => setIsExactModalOpen(false);

  // Modal Submit Handlers - Recent
  const submitRecentModal = async () => {
    try {
      const days =
        recentDaysInput.trim() === "" ? null : parseInt(recentDaysInput);
      const limit =
        recentLimitInput.trim() === "" ? null : parseInt(recentLimitInput);
      let queryParams = new URLSearchParams();
      if (days !== null) queryParams.append("days", days);
      if (limit !== null) queryParams.append("limit", limit);

      const response = await fetch(
        `${BASE_URL}/api/anki_import_recent?${queryParams.toString()}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await response.json();
      fetchWords();
      closeRecentModal();
    } catch (error) {
      console.error("Error importing recent cards:", error);
    }
  };

  // Modal Submit Handlers - Difficult
  const submitDifficultModal = async () => {
    try {
      const limit =
        difficultLimitInput.trim() === ""
          ? null
          : parseInt(difficultLimitInput);
      const reps =
        difficultRepsInput.trim() === "" ? null : parseInt(difficultRepsInput);
      const ease =
        difficultEaseInput.trim() === ""
          ? null
          : parseFloat(difficultEaseInput);
      let queryParams = new URLSearchParams();
      if (limit !== null) queryParams.append("limit", limit);
      if (reps !== null) queryParams.append("reps", reps);
      if (ease !== null) queryParams.append("ease", ease);

      const response = await fetch(
        `${BASE_URL}/api/anki_import_difficult?${queryParams.toString()}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await response.json();
      fetchWords();
      closeDifficultModal();
    } catch (error) {
      console.error("Error importing difficult cards:", error);
    }
  };

  // Modal Submit Handlers - Exact
  const submitExactModal = async () => {
    try {
      const search = exactSearchInput.trim();
      const limit =
        exactLimitInput.trim() === "" ? null : parseInt(exactLimitInput);
      if (!search) {
        alert("Search term is required for exact match import.");
        return;
      }
      let queryParams = new URLSearchParams();
      queryParams.append("search", search);
      if (limit !== null) queryParams.append("limit", limit);

      const response = await fetch(
        `${BASE_URL}/api/anki_import_exact?${queryParams.toString()}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await response.json();
      fetchWords();
      closeExactModal();
    } catch (error) {
      console.error("Error importing exact match card:", error);
    }
  };

  const handleRemoveSelected = async () => {
    if (selectedWord) {
      try {
        const response = await fetch(`${BASE_URL}/api/remove_card`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ cardId: selectedWord.id }),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        await response.json();
        setSelectedWord(null);
        fetchWords();
      } catch (error) {
        console.error("Error removing card:", error);
      }
    }
  };

  const handleRemoveAll = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/remove_all_cards`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await response.json();
      setSelectedWord(null);
      fetchWords();
    } catch (error) {
      console.error("Error removing all cards:", error);
    }
  };

  const handleOpenInAnki = async () => {
    if (selectedWord) {
      try {
        const response = await fetch(`${BASE_URL}/api/anki_open`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ cardId: selectedWord.id }),
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        await response.json();
        alert("Opened in Anki Browser");
      } catch (error) {
        console.error("Error opening in Anki:", error);
      }
    }
  };

  return (
    <BaseURLContext.Provider value={BASE_URL}>
      <div className="App">
        <div className="sidebar">
          <h3>Word List</h3>
          <div className="button-group">
            <button onClick={openRecentModal}>Add Recent</button>
            <button onClick={openDifficultModal}>Add Difficult</button>
            <button onClick={openExactModal}>Add Word</button>
          </div>
          {loadingWords ? (
            <p>Loading words...</p>
          ) : (
            <ul className="word-list">
              {words.map((word) => (
                <li
                  key={word.id}
                  className={
                    selectedWord && selectedWord.id === word.id
                      ? "selected"
                      : ""
                  }
                  onClick={() => handleWordSelect(word)}
                >
                  {word.word}
                </li>
              ))}
            </ul>
          )}

          <div className="button-group bottom-buttons">
            <button onClick={handleRemoveSelected} disabled={!selectedWord}>
              Remove Selected
            </button>
            <button onClick={handleRemoveAll}>Remove All</button>
            <button onClick={handleOpenInAnki} disabled={!selectedWord}>
              Open in Anki
            </button>
          </div>
        </div>

        <div className="main-view">
          <div className="top-bar">
            <button>Next</button>
            <button>AI History</button>
          </div>
          <div className="tab-bar">
            <button
              className={currentTab === "sentences" ? "active" : ""}
              onClick={() => handleTabChange("sentences")}
            >
              Sentences
            </button>
            <button
              className={currentTab === "sentence-meaning" ? "active" : ""}
              onClick={() => handleTabChange("sentence-meaning")}
            >
              Sentence-&gt;Meaning
            </button>
            <button
              className={currentTab === "word-meaning" ? "active" : ""}
              onClick={() => handleTabChange("word-meaning")}
            >
              Word-&gt;Pick correct meaning
            </button>
            <button
              className={currentTab === "meaning-word" ? "active" : ""}
              onClick={() => handleTabChange("meaning-word")}
            >
              Meaning-&gt;Word
            </button>
          </div>

          <div className="tab-content">
            {currentTab === "sentences" && (
              <TabModeSentencesComponent selectedWord={selectedWord} />
            )}
            {currentTab === "sentence-meaning" && (
              <div>
                <h4>Sentence-&gt;Meaning (Tab Content Stub)</h4>
                {selectedWord && words.length > 0 ? (
                  <p>
                    Example content for Sentence-&gt;Meaning for{" "}
                    {selectedWord.word}
                  </p>
                ) : (
                  <p>Select a word and have sentences to see content here.</p>
                )}
              </div>
            )}
            {currentTab === "word-meaning" && (
              <div>
                <h4>Word-&gt;Pick correct meaning (Tab Content Stub)</h4>
                <p>Content for Word-&gt;Pick correct meaning tab</p>
              </div>
            )}
            {currentTab === "meaning-word" && (
              <div>
                <h4>Meaning-&gt;Word (Tab Content Stub)</h4>
                <p>Content for Meaning-&gt;Word tab</p>
              </div>
            )}
          </div>

          <div className="status-bar">Status Bar (Placeholder)</div>
        </div>

        {/* Recent Cards Modal */}
        {isRecentModalOpen && (
          <div className="modal-backdrop">
            <div className="modal-content">
              <h3>Add Recent Cards</h3>
              <div className="modal-field">
                <label htmlFor="recent-days">Days:</label>
                <input
                  type="number"
                  id="recent-days"
                  value={recentDaysInput}
                  onChange={(e) => setRecentDaysInput(e.target.value)}
                />
              </div>
              <div className="modal-field">
                <label htmlFor="recent-limit">Limit:</label>
                <input
                  type="number"
                  id="recent-limit"
                  value={recentLimitInput}
                  onChange={(e) => setRecentLimitInput(e.target.value)}
                />
              </div>
              <div className="modal-buttons">
                <button onClick={submitRecentModal}>Add</button>
                <button onClick={closeRecentModal}>Cancel</button>
              </div>
            </div>
          </div>
        )}

        {/* Difficult Cards Modal */}
        {isDifficultModalOpen && (
          <div className="modal-backdrop">
            <div className="modal-content">
              <h3>Add Difficult Cards</h3>
              <div className="modal-field">
                <label htmlFor="difficult-limit">Limit:</label>
                <input
                  type="number"
                  id="difficult-limit"
                  value={difficultLimitInput}
                  onChange={(e) => setDifficultLimitInput(e.target.value)}
                />
              </div>
              <div className="modal-field">
                <label htmlFor="difficult-reps">Reps:</label>
                <input
                  type="number"
                  id="difficult-reps"
                  value={difficultRepsInput}
                  onChange={(e) => setDifficultRepsInput(e.target.value)}
                />
              </div>
              <div className="modal-field">
                <label htmlFor="difficult-ease">Ease:</label>
                <input
                  type="number"
                  id="difficult-ease"
                  value={difficultEaseInput}
                  onChange={(e) => setDifficultEaseInput(e.target.value)}
                />
              </div>
              <div className="modal-buttons">
                <button onClick={submitDifficultModal}>Add</button>
                <button onClick={closeDifficultModal}>Cancel</button>
              </div>
            </div>
          </div>
        )}

        {/* Exact Match Card Modal */}
        {isExactModalOpen && (
          <div className="modal-backdrop">
            <div className="modal-content">
              <h3>Add Word</h3>
              <div className="modal-field">
                <label htmlFor="exact-search">Search Term:</label>
                <input
                  type="text"
                  id="exact-search"
                  value={exactSearchInput}
                  onChange={(e) => setExactSearchInput(e.target.value)}
                />
              </div>
              <div className="modal-field">
                <label htmlFor="exact-limit">Limit:</label>
                <input
                  type="number"
                  id="exact-limit"
                  value={exactLimitInput}
                  onChange={(e) => setExactLimitInput(e.target.value)}
                />
              </div>
              <div className="modal-buttons">
                <button onClick={submitExactModal}>Add</button>
                <button onClick={closeExactModal}>Cancel</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </BaseURLContext.Provider>
  );
}

export default App;
