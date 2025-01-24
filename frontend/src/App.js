import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [words, setWords] = useState([]);
    const [selectedWord, setSelectedWord] = useState(null);
    const [sentences, setSentences] = useState([]);
    const [currentTab, setCurrentTab] = useState('sentences'); // Default tab
    const [loadingWords, setLoadingWords] = useState(false);

    const fetchWords = async () => {
        setLoadingWords(true);
        try {
            const response = await fetch('http://localhost:5001/api/words'); // Backend is now on port 5001
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
        fetchWords(); // Initial fetch of words
    }, []);

    useEffect(() => {
        if (selectedWord) {
            fetch(`http://localhost:5001/api/sentences/${selectedWord.word}`)
                .then(response => response.json())
                .then(data => setSentences(data))
                .catch(error => console.error("Could not fetch sentences:", error));
        } else {
            setSentences([]);
        }
    }, [selectedWord]);

    const handleWordSelect = (word) => {
        setSelectedWord(word);
    };

    const handleTabChange = (tabName) => {
        setCurrentTab(tabName);
    };

    const handleAddRecent = async () => {
        try {
            const response = await fetch('http://localhost:5001/api/anki_import_recent');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await response.json(); // Or handle response data if needed
            fetchWords(); // Refresh word list after import
        } catch (error) {
            console.error("Error importing recent cards:", error);
        }
    };

    const handleAddDifficult = async () => {
        try {
            const response = await fetch('http://localhost:5001/api/anki_import_difficult');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await response.json();
            fetchWords();
        } catch (error) {
            console.error("Error importing difficult cards:", error);
        }
    };

    const handleAddWord = async () => {
        const searchTerm = prompt("Enter word to search in Anki:");
        if (searchTerm) {
            try {
                const response = await fetch(`http://localhost:5001/api/anki_import_exact?search=${encodeURIComponent(searchTerm)}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                await response.json();
                fetchWords();
            } catch (error) {
                console.error("Error importing exact match card:", error);
            }
        }
    };

    const handleRemoveSelected = async () => {
        if (selectedWord) {
            try {
                const response = await fetch('http://localhost:5001/api/remove_card', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ cardId: selectedWord.id }),
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                await response.json();
                setSelectedWord(null); // Clear selection after removal
                fetchWords();
            } catch (error) {
                console.error("Error removing card:", error);
            }
        }
    };

    const handleRemoveAll = async () => {
        try {
            const response = await fetch('http://localhost:5001/api/remove_all_cards', {
                method: 'POST',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await response.json();
            setSelectedWord(null); // Clear selection after removal
            fetchWords();
        } catch (error) {
            console.error("Error removing all cards:", error);
        }
    };


    const handleOpenInAnki = async () => {
        if (selectedWord) {
            try {
                const response = await fetch('http://localhost:5001/api/anki_open', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ cardId: selectedWord.id }),
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                await response.json();
                alert("Opened in Anki Browser"); // Simple feedback
            } catch (error) {
                console.error("Error opening in Anki:", error);
            }
        }
    };


    return (
        <div className="App">
            <div className="sidebar">
                <h3>Word List</h3>
                <div className="button-group">
                    <button onClick={handleAddRecent}>Add Recent</button>
                    <button onClick={handleAddDifficult}>Add Difficult</button>
                    <button onClick={handleAddWord}>Add Word</button>
                </div>
                {loadingWords ? <p>Loading words...</p> : (
                    <ul className="word-list">
                        {words.map(word => (
                            <li
                                key={word.id}
                                className={selectedWord && selectedWord.id === word.id ? 'selected' : ''}
                                onClick={() => handleWordSelect(word)}
                            >
                                {word.word}
                            </li>
                        ))}
                    </ul>
                )}

                <div className="button-group bottom-buttons">
                    <button onClick={handleRemoveSelected} disabled={!selectedWord}>Remove Selected</button>
                    <button onClick={handleRemoveAll}>Remove All</button>
                    <button onClick={handleOpenInAnki} disabled={!selectedWord}>Open in Anki</button>
                </div>
            </div>

            <div className="main-view">
                <div className="top-bar">
                    <button>Next</button>
                    <button>AI History</button>
                </div>
                <div className="tab-bar">
                    <button className={currentTab === 'sentences' ? 'active' : ''} onClick={() => handleTabChange('sentences')}>Sentences</button>
                    <button className={currentTab === 'sentence-meaning' ? 'active' : ''} onClick={() => handleTabChange('sentence-meaning')}>Sentence->Meaning</button>
                    <button className={currentTab === 'word-meaning' ? 'active' : ''} onClick={() => handleTabChange('word-meaning')}>Word->Pick correct meaning</button>
                    <button className={currentTab === 'meaning-word' ? 'active' : ''} onClick={() => handleTabChange('meaning-word')}>Meaning->Word</button>
                </div>

                <div className="tab-content">
                    {currentTab === 'sentences' && (
                        <div>
                            <h4>Sentences for {selectedWord ? selectedWord.word : 'Select a word'}</h4>
                            <ul className="sentence-list">
                                {sentences.map(sentenceObj => (
                                    <li key={sentenceObj.id}>
                                        {sentenceObj.sentence} <button>AI Read</button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {currentTab === 'sentence-meaning' && (
                        <div>
                            {/* Content for Sentence->Meaning tab */}
                            <h4>Sentence->Meaning (Tab Content Stub)</h4>
                            {selectedWord && sentences.length > 0 ? (
                                <p>Example content for Sentence->Meaning for {selectedWord.word}</p>
                            ) : (
                                <p>Select a word and have sentences to see content here.</p>
                            )}
                        </div>
                    )}
                    {currentTab === 'word-meaning' && (
                        <div>
                            {/* Content for Word->Pick correct meaning tab */}
                            <h4>Word->Pick correct meaning (Tab Content Stub)</h4>
                            <p>Content for Word->Pick correct meaning tab</p>
                        </div>
                    )}
                    {currentTab === 'meaning-word' && (
                        <div>
                            {/* Content for Meaning->Word tab */}
                            <h4>Meaning->Word (Tab Content Stub)</h4>
                            <p>Content for Meaning->Word tab</p>
                        </div>
                    )}
                </div>

                <div className="status-bar">
                    Status Bar (Placeholder)
                </div>
            </div>
        </div>
    );
}

export default App;