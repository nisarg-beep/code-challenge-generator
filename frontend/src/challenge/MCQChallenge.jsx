import React, { useState, useEffect } from 'react';

export function MCQChallenge({ challenge, showExplanation = false }) {
    const [selectedOption, setSelectedOption] = useState(null);
    const [isSubmitted, setIsSubmitted] = useState(false);

    useEffect(() => {
        setSelectedOption(null);
        setIsSubmitted(false);
    }, [challenge]);

    // Clean up backticks at the frontend level just in case
    const formatQuestionText = (text) => {
        if (!text) return "";
        return text.replace(/```[a-z]*|```/g, '').trim();
    };

    if (!challenge) return null;

    // --- DATA PARSING SAFETY CHECK ---
    let options = [];
    try {
        // If options is a string (common from DB), parse it. If it's already an array, use it.
        options = typeof challenge.options === 'string'
            ? JSON.parse(challenge.options)
            : (Array.isArray(challenge.options) ? challenge.options : []);
    } catch (e) {
        console.error("Critical error parsing options:", e);
        options = []; // Fallback to empty list to prevent .map() crash
    }

    const cleanBody = formatQuestionText(challenge.question || challenge.title);

    const handleOptionSelect = (index) => {
        if (isSubmitted && !showExplanation) return;
        setSelectedOption(index);
        setIsSubmitted(true);
    };

    return (
        <div className="challenge-display">
            <div className="challenge-header">
                <span className="difficulty-label">Difficulty: {challenge.difficulty}</span>
                <h3 className="challenge-title">{challenge.title}</h3>
            </div>

            <div className="challenge-question-body">
                <p style={{ marginBottom: '8px', fontWeight: 'normal' }}>
                    Consider the following question:
                </p>
                <span className="question-text" style={{ fontWeight: 'bold', display: 'block' }}>
                    "{cleanBody}"
                </span>
            </div>

            <div className="options">
                {options.length > 0 ? options.map((option, index) => {
                    let optionClass = "option";
                    if (isSubmitted) {
                        if (index === challenge.correct_answer_id) optionClass += " correct";
                        else if (index === selectedOption) optionClass += " wrong";
                    } else if (selectedOption === index) {
                        optionClass += " selected";
                    }

                    return (
                        <div key={index} className={optionClass} onClick={() => handleOptionSelect(index)}>
                            {option}
                        </div>
                    );
                }) : <p>No options available for this challenge.</p>}
            </div>

            {(isSubmitted || showExplanation) && challenge.explanation && (
                <div className="explanation">
                    <h4>Explanation</h4>
                    <p>{challenge.explanation}</p>
                </div>
            )}
        </div>
    );
}