import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [words, setWords] = useState([]);
    const [selectedWord, setSelectedWord] = useState(null);
    const [sentences, setSentences] = useState([]);
    const [currentTab, setCurrentTab] = useState('sentences'); // Default tab

    useEffect(() => {
        fetch('http://localhost:5001/api/words') // Fetch words from backend
            .then(response => response.json())
            .then(data => setWords(data));
    }, []);

    useEffect(() => {
        if (selectedWord) {
            fetch('http://localhost:5001/api/sentences/${selectedWord.word}') // Fetch sentences for selected word
                .then(response => response.json())
                .then(data => setSentences(data));
        } else {
            setSentences([]); // Clear sentences if no word selected
        }
    }, [selectedWord]);

    const handleWordSelect = (word) => {
        setSelectedWord(word);
    };

    const handleTabChange = (tabName) => {
        setCurrentTab(tabName);
    };

    console.log(words)

    return (
        <div className="App">
            <div className="sidebar">
                <h3>Word List</h3>
                <div className="button-group">
                    <button>Add Recent</button>
                    <button>Add Difficult</button>
                    <button>Add Word</button>
                </div>
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
                <div className="button-group bottom-buttons">
                    <button disabled={!selectedWord}>Remove Selected</button>
                    <button disabled={!selectedWord}>Open in Anki</button>
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